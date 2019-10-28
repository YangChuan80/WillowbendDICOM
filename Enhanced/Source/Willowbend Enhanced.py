#!/usr/bin/env python
# coding: utf-8

# # Willowbend DICOM Enhanced
# <img src="Title.png" align="left" width="45%" height="45%">

# A dialog-based DICOM to video converter.
# 
# **DICOM (Digital Imaging and Communications in Medicine)** is a standard for handling, storing, printing, and transmitting information in medical imaging. DICOM files can be exchanged between two entities that are capable of receiving image and patient data in DICOM format by following network communications protocol. DICOM has been widely adopted by hospitals and is making inroads in smaller applications like dentists' and doctors' offices.
# 
# This project is to implement the process of conversion from DICOM format to video format (avi) in order to meet the needs and requirements for universal computer systems (PC, Mac, Linux, etc.). So the ordinary users of such systems can use the converted file to present, communicate and store the universal files. Case reports in medical conferences, educations of clinical medicine will become more convenient to use universal video formats in the slide presentations.

# ## Libraries

# In[1]:


import SimpleITK as sitk
import cv2
import pydicom
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog


# ## Helper Functions

# ### Basic Helper Functions

# In[2]:


def loadFile(filename):
    ds = sitk.ReadImage(filename)
    img_array = sitk.GetArrayFromImage(ds)
    frame_num, width, height = img_array.shape
    return img_array, frame_num, width, height


# In[3]:


def loadFileInformation(filename):
    information = {}
    ds = pydicom.read_file(filename)
    
    information['PatientID'] = ds.PatientID
    information['PatientName'] = ds.PatientName
    information['PatientBirthDate'] = ds.PatientBirthDate
    information['PatientSex'] = ds.PatientSex
    information['StudyID'] = ds.StudyID
    information['StudyDate'] = ds.StudyDate
    information['StudyTime'] = ds.StudyTime
    information['InstitutionName'] = ds.InstitutionName
    information['Manufacturer'] = ds.Manufacturer
    information['NumberOfFrames'] =ds.NumberOfFrames
    
    return information


# In[4]:


def autoEqualize(img_array):
    img_array_list = []
    for img in img_array:
        img_array_list.append(cv2.equalizeHist(img))
    img_array_equalized = np.array(img_array_list)
    return img_array_equalized


# In[5]:


def limitedEqualize(img_array, limit):
    img_array_list = []
    for img in img_array:
        clahe = cv2.createCLAHE(clipLimit=limit, tileGridSize=(8,8))  #CLAHE (Contrast Limited Adaptive Histogram Equalization)
        img_array_list.append(clahe.apply(img))
        
    img_array_limited_equalized = np.array(img_array_list, dtype=np.uint8)
    return img_array_limited_equalized   


# In[6]:


def writeVideo(img_array, directory, filename):
    frame_num, width, height = img_array.shape
    filename_output = directory + '/' + filename.split('.')[0].split('/')[-1] + '.avi'        
    
    #fourcc = cv2.VideoWriter_fourcc(*'XVID')
    #video = cv2.VideoWriter(filename_output, fourcc, 15, (width, height))
    # Above is for Mac OSX use only./////////////////////////////////////////////////////////////
    
    video = cv2.VideoWriter(filename_output, -1, 15, (width, height)) # Initialize Video File   
       
    for img in img_array:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        video.write(img_rgb) # Write video file frame by frame
        
    video.release()


# ## GUI Helper Function

# In[7]:


def browseFileButton():
    global filenames
    file_list = []
    
    try:
        filenames = filedialog.askopenfilenames(filetypes=(('DICOM files', '*.dcm'), ('All files', '*.*')))
        information = loadFileInformation(filenames[0])
        
        
        for filename in filenames:
            item = filename.split('/')[-1]
            file_list.append(item)

            file_list_str = str(file_list) + ' -- ' + str(len(filenames)) + ' files'
        
        # The files picked up are TUPLE!!!!!! ///////////////////////////

        text_filename.delete('1.0', tk.END)
        text_filename.insert('1.0', filenames[0])
        
        text_filenames.delete('1.0', tk.END)
        text_filenames.insert('1.0', file_list_str)

        text_PatientID.delete('1.0', tk.END)
        text_PatientID.insert('1.0', information['PatientID'])

        text_PatientName.delete('1.0', tk.END)
        text_PatientName.insert('1.0', information['PatientName'])

        text_PatientSex.delete('1.0', tk.END)
        text_PatientSex.insert('1.0', information['PatientSex'])

        text_PatientBirthDate.delete('1.0', tk.END)
        text_PatientBirthDate.insert('1.0', information['PatientBirthDate'])

        text_StudyID.delete('1.0', tk.END)
        text_StudyID.insert('1.0', information['StudyID'])

        text_StudyDate.delete('1.0', tk.END)
        text_StudyDate.insert('1.0', information['StudyDate'])

        text_StudyTime.delete('1.0', tk.END)
        text_StudyTime.insert('1.0', information['StudyTime'])

        text_InstitutionName.delete('1.0', tk.END)
        text_InstitutionName.insert('1.0', information['InstitutionName'])

        text_Manufacturer.delete('1.0', tk.END)
        text_Manufacturer.insert('1.0', information['Manufacturer'])

        text_NumberOfFrames.delete('1.0', tk.END)
        text_NumberOfFrames.insert('1.0', information['NumberOfFrames'])
        
        text_file_num.delete('1.0', tk.END)
        text_file_num.insert('1.0', len(filenames))
        
    except:
        filenames = {}


# In[8]:


def loadFileButton():
    global img_array, frame_num, width, height, information, isLoad
    img_array = {}
    frame_num = {}
    width = {}
    height = {}
    information = {}
    isLoad = {}
    
    if filenames == ():
        messagebox.showwarning("No File", "Sorry, no file loaded! Please choose DICOM file first.")
    else:
        try:
            for filename in filenames:                
                img_array[filename], frame_num[filename], width[filename], height[filename] = loadFile(filename)
                information[filename] = loadFileInformation(filename) 
                isLoad[filename] = 1
            messagebox.showinfo("DICOM File Loaded", "DICOM file successfully loaded!")
        except:
            messagebox.showwarning("File Loading Failed", "Sorry, file loading failed! Please check the file format.")


# In[9]:


def convertVideoButton():
    global isLoad, clipLimit
    #isLoad = {}
    
    clipLimit = float(text_clipLimit.get('1.0', tk.END))
    
    directory = filedialog.askdirectory()
    
    for filename in filenames:        
        if filename == '':
            messagebox.showwarning("No File to be Converted", "Sorry, no file to be converted! Please choose a DICOM file first.")
        elif isLoad[filename] == 0:
            messagebox.showwarning("No File Loaded", "Sorry, no file loaded! Please load the chosen DICOM file.")
        elif directory == '':
            messagebox.showwarning("No Directory", "Sorry, no directory shown! Please specify the output directory.")
        else:
            img_array_limited_equalized = limitedEqualize(img_array[filename], clipLimit)
            writeVideo(img_array_limited_equalized, directory, filename)
            #messagebox.showinfo("Video File Converted", "Video file successfully generated!")
            isLoad[filename] = 0
    messagebox.showinfo("Video File Converted", "Video(s) successfully converted!")


# In[10]:


def about():
    about_root=tk.Tk()
    
    w = 367 # width for the Tk root
    h = 230 # height for the Tk root

    # get screen width and height
    ws = about_root.winfo_screenwidth() # width of the screen
    hs = about_root.winfo_screenheight() # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)

    # set the dimensions of the screen 
    # and where it is placed
    about_root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    about_root.title('About Willowbend DICOM')  
    about_root.iconbitmap('Heart.ico')

    label_author=tk.Label(about_root,text='Willowbend DICOM Version 2.0', font=('tahoma', 9))
    label_author.place(x=90,y=30)

    label_author=tk.Label(about_root,text='Copyright (C) 2019', font=('tahoma', 9))
    label_author.place(x=125,y=60)
    
    label_author=tk.Label(about_root,text='Author: Chuan Yang', font=('tahoma', 9))
    label_author.place(x=125,y=90)
    
    label_author=tk.Label(about_root,text='Shengjing Hospital of China Medical University', font=('tahoma', 9))
    label_author.place(x=50,y=120)
   

    button_refresh=ttk.Button(about_root, width=15, text='OK', command=about_root.destroy)
    button_refresh.place(x=135, y=170)

    about_root.mainloop()


# ## Main Stream

# In[11]:


# Main Frame////////////////////////////////////////////////////////////////////////////////////////
root = tk.Tk()

w = 930 # width for the Tk root
h = 720 # height for the Tk root

# get screen width and height
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen

# calculate x and y coordinates for the Tk root window
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)

# set the dimensions of the screen 
# and where it is placed
root.geometry('%dx%d+%d+%d' % (w, h, x, y))
#root.attributes('-fullscreen', True)
root.title('Willowbend DICOM Enhanced')
root.iconbitmap('Heart.ico')

isLoad = {}
clipLimit = 2.0
filename = ''

# //////// Frame /////////////////////////////

label_Patients=tk.Label(root,width=125, height=43, font=('tahoma', 9), relief='raised', borderwidth=2)
label_Patients.place(x=20,y=15)

#///////////Image Title///////////////////////////////
photo=tk.PhotoImage(file='Title.png')
label_photo=tk.Label(root, image=photo, relief='sunken', borderwidth=3)
label_photo.place(x=260,y=35)

#/////////////Text///////////////////////////////////////////////////////////////////

text_PatientID=tk.Text(root, width=20,height=1, font=('tahoma', 9), bd=1)
text_PatientID.place(x=60, y=90)
label_PatientID=tk.Label(root, text='Patient ID', font=('tahoma', 9))
label_PatientID.place(x=60,y=60)

#//////////////////
y_position = 180
text_PatientName=tk.Text(root, width=30,height=1, font=('tahoma', 9), bd=1)
text_PatientName.place(x=60, y=y_position)
label_PatientName=tk.Label(root, text='Patient\'s Name:', font=('tahoma', 9))
label_PatientName.place(x=60,y=y_position-30)

text_PatientSex=tk.Text(root, width=15,height=1, font=('tahoma', 9), bd=1)
text_PatientSex.place(x=360, y=y_position)
label_PatientSex=tk.Label(root, text='Gender:', font=('tahoma', 9))
label_PatientSex.place(x=360,y=y_position-30)

text_PatientBirthDate=tk.Text(root, width=25,height=1, font=('tahoma', 9), bd=1)
text_PatientBirthDate.place(x=560, y=y_position)
label_PatientBirthDate=tk.Label(root, text='Birth Date:', font=('tahoma', 9))
label_PatientBirthDate.place(x=560,y=y_position-30)

#//////////////////////////////////////////////////////////////////////////////////
y_position = 250
text_StudyID=tk.Text(root, width=25,height=1, font=('tahoma', 9), bd=1)
text_StudyID.place(x=60, y=y_position)
label_StudyID=tk.Label(root, text='Study ID:', font=('tahoma', 9))
label_StudyID.place(x=60,y=y_position-30)

text_StudyDate=tk.Text(root, width=25,height=1, font=('tahoma', 9), bd=1)
text_StudyDate.place(x=340, y=y_position)
label_StudyDate=tk.Label(root, text='Study Date:', font=('tahoma', 9))
label_StudyDate.place(x=340,y=y_position-30)

text_StudyTime=tk.Text(root, width=25,height=1, font=('tahoma', 9), bd=1)
text_StudyTime.place(x=600, y=y_position)
label_StudyTime=tk.Label(root, text='Study Time:', font=('tahoma', 9))
label_StudyTime.place(x=600,y=y_position-30)

#////////////////////////////////////
y_position = 320
text_InstitutionName=tk.Text(root, width=50,height=1, font=('tahoma', 9), bd=1)
text_InstitutionName.place(x=60, y=y_position)
label_InstitutionName=tk.Label(root, text='Institution Name:', font=('tahoma', 9))
label_InstitutionName.place(x=60,y=y_position-30)

text_Manufacturer=tk.Text(root, width=38,height=1, font=('tahoma', 9), bd=1)
text_Manufacturer.place(x=560, y=y_position)
label_Manufacturer=tk.Label(root, text='Manufacturer:', font=('tahoma', 9))
label_Manufacturer.place(x=560,y=y_position-30)

# File Name
y_position = 390
text_filename=tk.Text(root, width=87,height=1, font=('tahoma', 9), bd=1)
text_filename.place(x=60, y=y_position)
label_filename=tk.Label(root, text='DICOM Directory:', font=('tahoma', 9))
label_filename.place(x=60,y=y_position-30)

text_NumberOfFrames=tk.Text(root, width=7,height=1, font=('tahoma', 9), bd=1)
text_NumberOfFrames.place(x=720, y=y_position)
label_NumberOfFrames=tk.Label(root, text='Frames', font=('tahoma', 9))
label_NumberOfFrames.place(x=790,y=y_position)

text_clipLimit=tk.Text(root, width=8,height=1, font=('tahoma', 9), bd=1)
text_clipLimit.place(x=580, y=560)
label_clipLimit=tk.Label(root, text='Clip Limit:', font=('tahoma', 9))
label_clipLimit.place(x=500,y=560)
text_clipLimit.delete('1.0', tk.END)
text_clipLimit.insert('1.0', clipLimit)

y_position = 429
text_filenames=tk.Text(root, width=112,height=7, font=('tahoma', 9), bd=1)
text_filenames.place(x=60, y=y_position)

text_file_num = tk.Text(root, width=6,height=1, font=('tahoma', 9), bd=1)
text_file_num.place(x=60, y=660)
label_file_num = tk.Label(root, text='files', font=('tahoma', 9))
label_file_num.place(x=120,y=660)

text_clipLimit.delete('1.0', tk.END)
text_clipLimit.insert('1.0', clipLimit)

#/////////////Button///////////////////////////////////////////////////////////////
button_browse=ttk.Button(root, text='Browse...', width=20, command=browseFileButton)
button_browse.place(x=60, y=565)

button_load=ttk.Button(root, text='Load', width=20, command=loadFileButton)
button_load.place(x=260, y=565)

button_convert=ttk.Button(root, text='Convert', width=20, command=convertVideoButton)
button_convert.place(x=700, y=565)

button_about=ttk.Button(root, text='About...', width=20, command=about)
button_about.place(x=260, y=660)

button_close=ttk.Button(root, width=20, text='Exit', command=root.destroy)
button_close.place(x=700, y=660)


# In[12]:


cv2.destroyAllWindows()


# In[13]:


root.mainloop()


# ### !!! Make sure to downgrade setuptools to 19.2. If this does get the frozen binary with PyInstaller !!!!
# Just hit this myself. Can confirm that downgrading to setuptools 19.2 fixes the issue for me.

# ### To install the SimpleITK package with conda run:
# 
# ```powershell
# conda install --channel https://conda.anaconda.org/SimpleITK SimpleITK
# ```

# ### The opencv should be the version of 3.4:
# ```
# pip install opencv-python==3.4.2.16
# ```
