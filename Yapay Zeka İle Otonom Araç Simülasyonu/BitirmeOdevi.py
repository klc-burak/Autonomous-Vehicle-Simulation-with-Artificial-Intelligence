# Gerekli Kütüphaneler
import math     # Matematiksel İşlemler
import sys      # Sistem İşlemleri (programın sonlandırılması vb.)
import neat     # NEAT
import pygame   # Grafik İşlemleri (simülasyonun oluşturulması)

# Araç Ölçeği (x ve y eksenlerine göre)
vehicleSize_X = 65
vehicleSize_Y = 65

# Harita Ölçeği
width = 1920
height = 1080

# İterasyon Sayacı
currentIteration = 0

# Yol Sınırı Rengi (aracın bu renge değmesi durumunda kaza gerçekleşir)
borderColor = (255, 255, 255, 255)     # (Beyaz)

# FPS Değeri
FPS = 120

# Toplam Kaza Sayısı, Toplam Mesafe ve Ortalama Hız
total_collisions = 0
total_distance = 0
average_speed = 0


class Vehicle:

    def __init__(vehicle):

        # Araç Görselinin Yüklenmesi ve Ölçeklenmesi
        vehicle.sprite = pygame.image.load('vehicle.png').convert()                                # Yükleme
        vehicle.sprite = pygame.transform.scale(vehicle.sprite, (vehicleSize_X, vehicleSize_Y))    # Ölçekleme
        vehicle.rotatedSprite = vehicle.sprite

        # Aracın Başlangıç Konumunun, Açısının ve Hızının Belirlenmesi
        vehicle.position = [860, 270]   # Başlangıç Konumu
        vehicle.speed = 0               # Başlangıç Hızı
        vehicle.angle = 0               # Başlangıç Açısı
        vehicle.speed_set = False

        # Araç Merkezinin Hesaplanması
        vehicle.center = [vehicle.position[0] + vehicleSize_X / 2, vehicle.position[1] + vehicleSize_Y / 2]

        # Sensörlerin Tanımlanması
        vehicle.sensors = []
        vehicle.drawingSensors = []

        vehicle.isAlive = True    # Aracın Kaza Yapıp Yapmadığının Kontrolü
        vehicle.distance = 0      # Alınan Mesafe
        vehicle.time = 0          # Geçen Süre

        # Maksimum ve Minimum Hız
        vehicle.max_speed = 0
        vehicle.min_speed = float('inf')

    def draw(vehicle, screen):          # Araç ve Sensörlerin Çizilmesi

        screen.blit(vehicle.rotatedSprite, vehicle.position)
        vehicle.drawSensor(screen)

    def drawSensor(vehicle, screen):    # Sensör Özellikleri

        for sensor in vehicle.sensors:
            position = sensor[0]
            pygame.draw.line(screen, (0, 255, 255), vehicle.center, position, 1)    # Sensör Çizgileri
            pygame.draw.circle(screen, (0, 255, 255), position, 5)                  # Sensör Uçları

    def checkCollision(vehicle, map):   # Çarpışma Kontrolü

        vehicle.isAlive = True
        for point in vehicle.corners:
            if map.get_at((int(point[0]), int(point[1]))) == borderColor:
                vehicle.isAlive = False
                break

    def checkSensors(vehicle, degree, map):     # Aracın Yol Sınırlarına Olan Mesafesinin Hesaplanması

        length = 0      # Sensör Başlangıç Uzunluğu

        # Aracın Merkezine Göre Sensörün İlk X ve Y Koordinatlarını Hesaplaması
        x = int(vehicle.center[0] + math.cos(math.radians(360 - (vehicle.angle + degree))) * length)
        y = int(vehicle.center[1] + math.sin(math.radians(360 - (vehicle.angle + degree))) * length)

        # Sensör Çizgisinin Yol Sınırına veya Belirlenmiş Maksimum Uzunluğa Kadar Uzatılması
        while not map.get_at((x, y)) == borderColor and length < 250:
            length = length + 1

            # Açıya Göre Yeni X ve Y Koordinatlarının Belirlenmesi
            x = int(vehicle.center[0] + math.cos(math.radians(360 - (vehicle.angle + degree))) * length)
            y = int(vehicle.center[1] + math.sin(math.radians(360 - (vehicle.angle + degree))) * length)

        # Sensör Noktası ile Araç Merkezi Arasındaki Mesafenin Hesaplanması
        distance = int(math.sqrt(math.pow(x - vehicle.center[0], 2) + math.pow(y - vehicle.center[1], 2)))
        vehicle.sensors.append([(x, y), distance])

    def update(vehicle, map):

        # Başlangıç Hızının Belirlenmesi
        if not vehicle.speed_set:
            vehicle.speed = 20
            vehicle.speed_set = True

        # Hız Değerlerinin Güncellenmesi
        vehicle.max_speed = max(vehicle.max_speed, vehicle.speed)
        vehicle.min_speed = min(vehicle.min_speed, vehicle.speed)

        # Konum Ve Açı Değerlerinin Güncellenmesi (X ekseni için)
        vehicle.rotatedSprite = vehicle.rotateCenter(vehicle.sprite, vehicle.angle)
        vehicle.position[0] += math.cos(math.radians(360 - vehicle.angle)) * vehicle.speed
        vehicle.position[0] = max(vehicle.position[0], 25)
        vehicle.position[0] = min(vehicle.position[0], width - 125)

        # Zaman ve Mesafe Değerlerinin Artırılması
        vehicle.time += 1
        vehicle.distance += vehicle.speed

        # Konum Ve Açı Değerlerinin Güncellenmesi (Y ekseni için)
        vehicle.position[1] += math.sin(math.radians(360 - vehicle.angle)) * vehicle.speed
        vehicle.position[1] = max(vehicle.position[1], 25)
        vehicle.position[1] = min(vehicle.position[1], width - 125)

        # Yeni Merkezin Hesaplanması
        vehicle.center = [int(vehicle.position[0]) + vehicleSize_X / 2, int(vehicle.position[1]) + vehicleSize_Y / 2]

        # Aracın Köşelerinin Belirlenmesi
        length = 0.5 * vehicleSize_X

        leftBottom = [vehicle.center[0] + math.cos(math.radians(360 - (vehicle.angle + 210))) * length,
                       vehicle.center[1] + math.sin(math.radians(360 - (vehicle.angle + 210))) * length]
        rightBottom = [vehicle.center[0] + math.cos(math.radians(360 - (vehicle.angle + 330))) * length,
                        vehicle.center[1] + math.sin(math.radians(360 - (vehicle.angle + 330))) * length]

        leftTop = [vehicle.center[0] + math.cos(math.radians(360 - (vehicle.angle + 30))) * length,
                    vehicle.center[1] + math.sin(math.radians(360 - (vehicle.angle + 30))) * length]
        rightTop = [vehicle.center[0] + math.cos(math.radians(360 - (vehicle.angle + 150))) * length,
                     vehicle.center[1] + math.sin(math.radians(360 - (vehicle.angle + 150))) * length]

        vehicle.corners = [leftTop, rightTop, leftBottom, rightBottom]

        # Çarpışmaların Kontrol Edilmesi ve Sensörlerin Temizlenmesi
        vehicle.checkCollision(map)
        if not vehicle.isAlive:
            global total_collisions
            total_collisions += 1
        vehicle.sensors.clear()

        for D in range(-90, 120, 45):
            vehicle.checkSensors(D, map)

    def getData(vehicle):       # Sınıra Olan Mesafenin Belirlenmesi

        sensors = vehicle.sensors
        return_values = [0, 0, 0, 0, 0]
        for i, sensor in enumerate(sensors):
            return_values[i] = int(sensor[1] / 30)
        return return_values

    def is_alive(vehicle):
        return vehicle.isAlive

    def getReward(vehicle):
        return vehicle.distance / (vehicleSize_X / 2)

    def rotateCenter(self, image, angle):
        rectangle = image.get_rect()
        rotatedImage = pygame.transform.rotate(image, angle)
        rotatedRectangle = rectangle.copy()
        rotatedRectangle.center = rotatedImage.get_rect().center
        rotatedImage = rotatedImage.subsurface(rotatedRectangle).copy()
        return rotatedImage


def runSimulation(genomes, config):

    global total_distance
    global average_speed

    nets = []
    cars = []

    # PyGame'in Başlatılması
    pygame.init()
    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)

    # Yeni Sinir Ağlarının Oluşturulması
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0
        cars.append(Vehicle())

    # Yol Haritasının Yüklenmesi ve Bilgi Fontlarının Belirlenmesi
    clock = pygame.time.Clock()
    map = pygame.image.load('map1.png').convert()
    font = pygame.font.SysFont("Arial Black", 20)

    global currentIteration
    currentIteration += 1

    counter = 0
    max_time = 0
    min_time = float('inf')

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # Herbir Araç İçin Gerekli Eylemin Belirlenmesi
        for i, car in enumerate(cars):
            output = nets[i].activate(car.getData())
            choice = output.index(max(output))
            if choice == 0:
                car.angle += 10             # Sol
            elif choice == 1:
                car.angle -= 10             # Sağ
            elif choice == 2:
                if(car.speed - 2 >= 12):
                    car.speed -= 2          # Yavaşlama
            else:
                car.speed += 2              # Hızlanma

        # Kaza Yapmamış Araçların Uygunluk Değerinin Artırılması ve Kaza Yapmış Araçların Döngüden Çıkarılması
        stillAlive = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                stillAlive += 1
                car.update(map)
                genomes[i][1].fitness += car.getReward()

        if stillAlive == 0:
            break

        counter += 1
        if counter == 30 * 40:              # İterasyonun 12 Saniye Sonra Durdurulması
            break

        # Kaza Yapmamış Araçların ve Haritanın Çizilmesi
        screen.blit(map, (0, 0))
        for car in cars:
            if car.is_alive():
                car.draw(screen)
            # Maksimum ve Minimum Zaman
            max_time = max(max_time, car.time)
            min_time = min(min_time, car.time)

        # Maksimum, Minimum ve Ortalama Fitness Değerlerinin Hesaplanması
        fitness_scores = [genomes[i][1].fitness for i in range(len(genomes))]
        max_fitness = max(fitness_scores)
        min_fitness = min(fitness_scores)
        avg_fitness = sum(fitness_scores) / len(fitness_scores)

        # Toplam Mesafenin ve Ortalama Hızın Hesaplanması
        total_distance = sum(car.distance for car in cars)
        average_speed = total_distance / max(car.time for car in cars if car.time > 0)

        # Bilgilerin Görüntülenmesi
        text = font.render("İterasyon: " + str(currentIteration), True, (255, 255, 255))    # İterasyon
        screen.blit(text, (840, 1025))

        text = font.render("Araç Sayısı: " + str(stillAlive), True, (255, 255, 255))        # Araç Sayısı
        screen.blit(text, (840, 1000))

        text = font.render(f"Maksimum Fitness: {max_fitness}", True, (255, 255, 255))       # Maksimum Fitness
        screen.blit(text, (375, 950))

        text = font.render(f"Minimum Fitness: {min_fitness}", True, (255, 255, 255))        # Minimum Fitness
        screen.blit(text, (375, 975))

        text = font.render(f"Ortalama Fitness: {avg_fitness:.2f}", True, (255, 255, 255))   # Ortalam Fitness
        screen.blit(text, (375, 1000))

        text = font.render(f"Toplam Mesafe: {total_distance:.2f}", True, (255, 255, 255))   # Toplam Mesafe
        screen.blit(text, (375, 1025))

        text = font.render(f"Ortalama Hız: {average_speed:.2f}", True, (255, 255, 255))     # Ortalama Hız
        screen.blit(text, (840, 950))

        text = font.render(f"Toplam Kaza: {total_collisions}", True, (255, 255, 255))       # Toplam Kaza
        screen.blit(text, (840, 975))

        max_speed = max(car.max_speed for car in cars)
        min_speed = min(car.min_speed for car in cars)

        # Maksimum Hız, Minimum Hız, Maksimum Süre, Minimum Süre ve FPS Değerlerinin Ekrana Yazdırılması
        text = font.render(f"Maksimum Başlangıç Hızı: {max_speed}", True, (255, 255, 255))  # Maksimum Başlangıç Hızı
        screen.blit(text, (25, 950))

        text = font.render(f"Minimum Başlangıç Hızı: {min_speed}", True, (255, 255, 255))   # Minimum Başlangıç Hızı
        screen.blit(text, (25, 975))

        text = font.render(f"Maksimum Süre: {max_time} ms", True, (255, 255, 255))          # Maksimum Süre
        screen.blit(text, (25, 1000))

        text = font.render(f"Minimum Süre: {min_time} ms", True, (255, 255, 255))           # Minimum Süre
        screen.blit(text, (25, 1025))

        text = font.render(f"FPS: {FPS}", True, (255, 255, 255))                            # FPS
        screen.blit(text, (1800, 10))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":

    # Config'in Yüklenmesi
    config_path = "./config.txt"
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Maksimum İterasyon Sayısının Belirlenmesi
    population.run(runSimulation, 100)
