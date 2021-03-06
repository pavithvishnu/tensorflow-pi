# Import required Python libraries
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
  
import serial
import argparse
import sys
import time
import RPi.GPIO as GPIO
import picamera
import datetime
import numpy as np
import tensorflow as tf
# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BOARD)
camera = picamera.PiCamera()

 
#ser=serial.Serial('/dev/ttyUSB0',9600,timeout=1)


# Define GPIO to use on Pi
GPIO_PIR = 7


print ("PIR Module Holding Time Test (CTRL-C to exit)")

# Set pin as input
GPIO.setup(GPIO_PIR,GPIO.IN)
GPIO.setup(20,GPIO.OUT)
#date=str(datetime.datetime.today())

Current_State  = 0
Previous_State = 0

def load_graph(model_file):
  graph = tf.Graph()
  graph_def = tf.GraphDef()

  with open(model_file, "rb") as f:
    graph_def.ParseFromString(f.read())
  with graph.as_default():
    tf.import_graph_def(graph_def)

  return graph

def read_tensor_from_image_file(file_name, input_height=299, input_width=299,
				input_mean=0, input_std=255):
  input_name = "file_reader"
  output_name = "normalized"
  file_reader = tf.read_file(file_name, input_name)
  if file_name.endswith(".png"):
    image_reader = tf.image.decode_png(file_reader, channels = 3,
                                       name='png_reader')
  elif file_name.endswith(".gif"):
    image_reader = tf.squeeze(tf.image.decode_gif(file_reader,
                                                  name='gif_reader'))
  elif file_name.endswith(".bmp"):
    image_reader = tf.image.decode_bmp(file_reader, name='bmp_reader')
  else:
    image_reader = tf.image.decode_jpeg(file_reader, channels = 3,
                                        name='jpeg_reader')
  float_caster = tf.cast(image_reader, tf.float32)
  dims_expander = tf.expand_dims(float_caster, 0);
  resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
  normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
  sess = tf.Session()
  result = sess.run(normalized)

  return result

def load_labels(label_file):
  label = []
  proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
  for l in proto_as_ascii_lines:
    label.append(l.rstrip())
  return label

try:

  print ("Waiting for PIR to settle ...")

  # Loop until PIR output is 0
  while GPIO.input(GPIO_PIR)==1:
    Current_State  = 0

  print ("Ready. No Motion Detected")

 # ser.write("AT+CMGF=1\r") # set to text mode
 # time.sleep(3)
 # ser.write('AT+CMGDA="DEL ALL"\r') # delete all SMS
 # time.sleep(3)

  # Loop until users quits with CTRL-C
  while True :

    # Read PIR state
    Current_State = GPIO.input(GPIO_PIR)

    if Current_State==1 and Previous_State==0:
      # PIR is triggered
     
      start_time=time.time()
      camera.start_preview()
      time.sleep(1)
      camera.capture('image.jpg')
      camera.stop_preview()
      date=str(datetime.datetime.today())
      camera.capture("/home/pi/Desktop/Gold/Images/"+'image'+date+'.jpg')
      print ("  Motion detected! A picture has been taken  \n  Proccesing image  ")
      # Record previous state
      file_name = "image.jpg"
    # set the image for classification to image1.jpg as we just captured from pi camera!
      model_file = "inception_v3_2016_08_28_frozen.pb"
      label_file = "labels_incep.txt"
      input_height = 299
      input_width = 299
      input_mean = 0
      input_std = 255
      input_layer = "input"
      output_layer = "InceptionV3/Predictions/Reshape_1"
      graph = load_graph(model_file)
      t = read_tensor_from_image_file(file_name,
                                    input_height=input_height,
                                    input_width=input_width,
                                    input_mean=input_mean,
                                    input_std=input_std)
      input_name = "import/" + input_layer
      output_name = "import/" + output_layer
      input_operation = graph.get_operation_by_name(input_name);
      output_operation = graph.get_operation_by_name(output_name);
      
      with tf.Session(graph=graph) as sess:
          results = sess.run(output_operation.outputs[0],{input_operation.outputs[0]: t})
          results = np.squeeze(results)
          
      top_k = results.argsort()[-5:][::-1]
      labels = load_labels(label_file)
      # we are just taking the top result and its label
      first = top_k[0]
      top_label = str(labels[first])
      top_result = str(results[first])
      print(top_label)
      print(top_result)
      if top_label == ("Indian elephant"):
        GPIO.output(20,GPIO.HIGH)
        time.sleep(1)
        GPIO.output(20,GPIO.LOW)
        time.sleep(1)
        
        print ("Message Sent")
     #   ser.write('AT+CMGS="+919751896988"\r')
     #   time.sleep(5)
        msg = "Elephant has been detected at camera 3"
         #print "Sending SMS" +top_label
     #   ser.write(msg + chr(26))
      #  time.sleep(3)
     #   ser.write('AT+CMGDA="DEL ALL"\r') # delete all
     #   time.sleep(3)
      elif top_label == ("African elephant"):
        GPIO.output(20,GPIO.HIGH)
        time.sleep(1)
        GPIO.output(20,GPIO.LOW)
        time.sleep(1)
        
        
        print ("Message Sent")
     #   ser.write('AT+CMGS="+919751896988"\r')
     #   time.sleep(3)
        msg = "Elephant has been detected at camera 3"
         #print "Sending SMS" +top_label
     #   ser.write(msg + chr(26))
     #   time.sleep(3)
     #   ser.write('AT+CMGDA="DEL ALL"\r') # delete all
     #   time.sleep(3)
      elif top_label == ("tusker"):
        GPIO.output(20,GPIO.HIGH)
        time.sleep(1)
        GPIO.output(20,GPIO.LOW)
        time.sleep(1)

        
        print ("Message Sent")
     #   ser.write('AT+CMGS="+919751896988"\r')
    #    time.sleep(3)
        msg = "Elephant has been detected at camera 3"
         #print "Sending SMS" +top_label
    #    ser.write(msg + chr(26))
    #    time.sleep(3)
    #    ser.write('AT+CMGDA="DEL ALL"\r') # delete all
    #    time.sleep(3)
        
      else:
        print ("Continuing Process")
      
      Previous_State=1
    elif Current_State==0 and Previous_State==1:
      # PIR has returned to ready state
      stop_time=time.time()
      print ("  Ready. No Motion Detected ")
      elapsed_time=int(stop_time-start_time)
      print (" (Elapsed time : " + str(elapsed_time) + " secs)")
      Previous_State=0

except KeyboardInterrupt:
  print ("  Quit")
  # Reset GPIO settings
  GPIO.cleanup()
