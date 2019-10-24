import sensor
import image
import lcd
import random
import KPU as kpu
import utime
from Maix import GPIO
from board import board_info
from fpioa_manager import *
from pmu import axp192
pmu = axp192()
#enables the on/off (sleep) button 
pmu.enablePMICSleepMode(True)
#enable the voltage monitor
pmu.enableADCs(True)
#register buttons & leds
fm.register(board_info.BUTTON_A, fm.fpioa.GPIO1)
but_a=GPIO(GPIO.GPIO1, GPIO.IN, GPIO.PULL_UP)
if but_a.value() == 0:
	sys.exit()
fm.register(board_info.BUTTON_B, fm.fpioa.GPIO2)
but_b = GPIO(GPIO.GPIO2, GPIO.IN, GPIO.PULL_UP)
fm.register(board_info.LED_W, fm.fpioa.GPIO3)
led_w = GPIO(GPIO.GPIO3, GPIO.OUT)
led_w.value(1)
fm.register(board_info.LED_R, fm.fpioa.GPIO4)
led_r = GPIO(GPIO.GPIO4, GPIO.OUT)
led_r.value(1)
fm.register(board_info.LED_G, fm.fpioa.GPIO5)
led_g = GPIO(GPIO.GPIO5, GPIO.OUT)
led_g.value(1)
fm.register(board_info.LED_B, fm.fpioa.GPIO6)
led_b = GPIO(GPIO.GPIO6, GPIO.OUT)
led_b.value(1)
#wait a bit
time.sleep(0.5)
#buttons control
but_stu = 1
#init lcd
lcd.init()
#rotate 180
lcd.rotation(2)
#boot image
img = image.Image("/sd/logoNEW.jpg")
# display image on top
lcd.display(img)
#keep image for 2 sec 
time.sleep(2)
#start camera sensor
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.run(1)
#init the neural net - 0x300000 is the memory location of the face detection model that came with the board
task = kpu.load(0x300000)
#classes of the model (currently not used)
classes = ['aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus', 'car', 'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse', 'motorbike', 'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tvmonitor']
#model wont work if u dont upload the model alongside
#taskalt = kpu.load("/sd/model/20class.kmodel")
anchor = (1.889, 2.5245, 2.9465, 3.94056, 3.99987, 5.3658, 5.155437, 6.92275, 6.718375, 9.01025)
#yolo is you only  look once -read more here: https://pjreddie.com/darknet/yolo/
a = kpu.init_yolo2(task, 0.5, 0.3, 5, anchor)
#kpu.init_yolo2(taskalt, 0.5, 0.3, 5, anchor)
#while loop 
while(True):
	#take a picture and save it in micropython heap memory 
	img = sensor.snapshot()
	#check picture with neural network
	code = kpu.run_yolo2(task, img)
	#code_obj = kpu.run_yolo2(taskalt, img)
	#overlay image on top of camera view
	#img.draw_image(image.Image("/sd/face.jpg"),90,50)
	#if led_w.value() == 0:
	#	img.draw_image(image.Image("/sd/facej.jpg"),175,100,mask=image.Image("/sd/face-maskj.jpg"))
	#if code has returns a result
	if code:
		#img.draw_string(lcd.width()//2-10,lcd.height()//2-4, "")
		for i in code:
			#save % of certaintly of the neural net for the result 
			text = ' Person: (' + str(int(i.value()*100)) + '%) '
			print(i)
			#pre-check the size of the item identified (face box in this case) and save a scale (float) size
			if (i.w() < 40):
				scalx = 0.5
				scaly = 0.5
			elif (i.w() < 80):
				scalx = 1.2
				scaly = 1.2
			else:
				scalx = 1.5
				scaly = 1.5
			#embed on top of the image saved in the micropython memory heap a picture of joker that is also scaled as close as possible to the face 	
			img.draw_image(image.Image("/sd/facej.jpg"),i.x(),i.y(),x_scale=scalx,y_scale=scaly,mask=image.Image("/sd/face-maskj.jpg"))
			#a = img.draw_rectangle(i.rect())
			#path = "/sd/image"+str(random.randrange(1, 1000))+"c"+str(random.randrange(1, 99))+".jpg"
			#img.save(path)
			#print("saved image with name: "+path)
			#for x in range(-1,2):
				#for y in range(-1,2):
					#img.draw_string(x+i.x(), y+i.y()+(i.h()>>1), text, color=(250,205,137), scale=2,mono_space=False)
			#img.draw_string(i.x(), i.y()+(i.h()>>1), text, color=(119,48,48), scale=2,mono_space=False)
	#display on lcd the final result (not optimised low framerate)		
	a = lcd.display(img)
	#buttons check for interaction  button A -> white led, button B -> show battery temp currently
	if but_a.value() == 0 and but_stu == 1:
		if led_w.value() == 1:
			led_w.value(0)
		else:
			led_w.value(1)
		but_stu = 0
	if but_a.value() == 1 and but_stu == 0:
		but_stu = 1
	if but_b.value() == 0:
		#python lcd draw string fucntion 
		lcd.draw_string(lcd.width()//2-100,lcd.height()//3-4, " "+str(pmu.getTemperature())+"C  ", lcd.WHITE, lcd.RED)
		#lcd.draw_string(lcd.width()//2-100,lcd.height()//2-4, " "+str(pmu.getBatteryDischargeCurrent())+" ", lcd.WHITE, lcd.RED)
		a = lcd.display(img)
		time.sleep(0.1)
#loop ends repeat forever until poweroff 		
a = kpu.deinit(task)
sys.exit()
