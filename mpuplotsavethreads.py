from BNO055 import BNO055
import threading
import time
import csv
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class savingDataThread(threading.Thread):
   def __init__(self, filename):
      threading.Thread.__init__(self)
      self.t0 = time.time()
      self.filename=filename
      self.fieldnames=["time", "yaw", "pitch", "roll"]
      with open(filename, 'w') as csv_file:
          csv_writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
          csv_writer.writeheader()
   def run(self):
      print("Starting saving data")
      while acquisition:
          a = bno.getVector(BNO055.VECTOR_EULER)
          t=time.time()-self.t0
          # Get lock to protect file
          threadLock.acquire()
          with open(self.filename, 'a') as csv_file:
              csv_writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
              info = {
                  "time": t,
                  "yaw": a[0],
                  "pitch": a[1],
                  "roll": a[2]
                  }
              # Free lock to release next thread
              threadLock.release()
              csv_writer.writerow(info)
              time.sleep(0.02)

class plottingDataThread(threading.Thread):
   def __init__(self, filename,timeWindow):
      threading.Thread.__init__(self)
      self.filename=filename
      self.fieldnames=['time', "yaw", "pitch", "roll"]
      self.timeWindow=timeWindow
   def run(self):
      print("Starting plotting data")
      plt.ion()
      while acquisition:
          threadLock.acquire()
          data = pd.read_csv(filename)
          tend = data['time'].iloc[-1]
          t=data[data['time']>=tend-self.timeWindow]['time']
          ax = data[data['time']>=tend-self.timeWindow]['yaw']
          ay = data[data['time']>=tend-self.timeWindow]['pitch']
          az = data[data['time']>=tend-self.timeWindow]['roll']
            
##          ax = data['ax']
##          ay = data['ay']
##          az = data['az']
          threadLock.release()
          
          tend=t.iloc[-1]

          plt.cla()
          
          plt.plot(t, ax, label='Yaw')
          plt.plot(t, ay, label='Pitch')
          plt.plot(t, az, label='Roll')
          
          plt.legend(loc='upper left')
          plt.xlim(tend-self.timeWindow,tend)
          #plt.tight_layout()
          plt.show()
          plt.pause(0.1)
              
if __name__ == '__main__':
    bno = BNO055()
    if bno.begin() is not True:
            print("Error initializing device")
            exit()
    time.sleep(1)
    bno.setExternalCrystalUse(True)
    threadLock = threading.Lock()
    global acquisition
    threads=[]

    plt.style.use('fivethirtyeight')
    filename='test.csv'

    acquisition=True
    # Create new threads
    thread1 = savingDataThread(filename)
    thread2 = plottingDataThread(filename,5)
    # Start new Threads
    thread1.start()
    time.sleep(0.5)
    thread2.start()

    # Add threads to thread list
    threads.append(thread1)
    threads.append(thread2)

    time.sleep(1)
    input("press enter")
    acquisition=False
    # Wait for all threads to complete
    for t in threads:
        t.join()

    print('bye ...')

    ##try:
    ##  while True:
    ##            time.sleep(0.5)   
    ##      
    ##except KeyboardInterrupt:
    ##    acquisition = False
    ##    print('bye ...')
    ##  
    ##




