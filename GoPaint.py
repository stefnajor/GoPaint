#### GoPaint
#
# by Gary O'Brien
# - Summer 2021

import numpy as np
import cv2
import math

# Globals Init
prevX = 0
prevY = 0
colorPicked = [0,0,0]
painting = False
brushSize = 7
bucketQueue = []
tool = 0  # 0: brush, 1: fill, 2: rectangle, 3: circle, 4: line, 5: eyedropper
saveState = np.zeros((512,512,3)) + 255

def bucket_tool(x, y, oldColor):
    global colorPicked, bucketQueue

    if (x < 0 or x > img.shape[1] or y < 44 or y > img.shape[0]): return
    if oldColor[0] == colorPicked[0] and oldColor[1] == colorPicked[1] and oldColor[2] == colorPicked[2]: return

    bucketQueue.append(tuple((x,y)))

    while bucketQueue:
        curX, curY = bucketQueue[0]
        bucketQueue.pop(0)

        if (img[curY,curX,0] == oldColor[0] and img[curY,curX,1] == oldColor[1] and img[curY,curX,2] == oldColor[2]):
            img[curY,curX] = colorPicked
            if (curX + 1 < img.shape[1]): 
                bucketQueue.append(tuple((curX+1,curY)))
            if (curY + 1 < img.shape[0]): 
                bucketQueue.append(tuple((curX,curY+1)))
            if (curX - 1 >= 0): 
                bucketQueue.append(tuple((curX-1,curY)))
            if (curY - 1 >= 44): 
                bucketQueue.append(tuple((curX,curY-1)))

def mouseDriver(event,x,y,flags,param):
    global painting, colorPicked, brushSize, prevX, prevY, tool, saveState

    # Mousewheel
    if event == 10 and not painting:
        if flags > 0 and brushSize < 99: # wheel up
            brushSize += 1
            img[24:40, 200:224] = [180,180,180]
            cv2.putText(img, str(brushSize), (199, 38), cv2.FONT_HERSHEY_SIMPLEX, .61, (0, 0, 0), 1)
        elif flags < 0 and brushSize > 1: # wheel down
            brushSize -= 1
            img[24:40, 200:224] = [180,180,180]
            cv2.putText(img, str(brushSize), (199, 38), cv2.FONT_HERSHEY_SIMPLEX, .61, (0, 0, 0), 1)

    # Mouse Moved
    if event == cv2.EVENT_MOUSEMOVE:
        # Only draw when pen is fully inside canvas and LMB is pressed
        if (painting and y > (43 + math.ceil(brushSize / 2))):
            if (tool == 0):
                cv2.line(img,(prevX, prevY),(x,y),thickness=brushSize,color=(int(colorPicked[0]), int(colorPicked[1]), int(colorPicked[2])))
                prevX = x
                prevY = y
            elif (tool == 2):
                img[44:,:] = saveState
                cv2.rectangle(img, (prevX, prevY), (x,y), thickness=brushSize,color=(int(colorPicked[0]), int(colorPicked[1]), int(colorPicked[2])))
            elif (tool == 3):
                img[44:,:] = saveState
                midX = (x + prevX) // 2
                midY = (y + prevY) // 2
                cv2.ellipse(img, (midX, midY), (abs(x - prevX)//2, abs(y - prevY)//2), 
                    angle=0, startAngle=0, endAngle=360, 
                    thickness=brushSize,
                    color=(int(colorPicked[0]), int(colorPicked[1]), int(colorPicked[2])))
            elif (tool == 4):
                img[44:,:] = saveState
                cv2.line(img, (prevX, prevY), (x,y),  thickness=brushSize,color=(int(colorPicked[0]), int(colorPicked[1]), int(colorPicked[2])))

    # Left Click Released
    if event == cv2.EVENT_LBUTTONUP:
        painting = False

    # Left Click Pressed
    if event == cv2.EVENT_LBUTTONDOWN:
        # If mouse is within canvas area @ img[44:, :]
        if (y > 44):
            saveState = np.array(img[44:, :])
            # If brush is selected and mouse is within edge of canvas with respect to brush size
            if (tool == 0 and y > (44 + math.ceil(brushSize / 2))):
                if (brushSize > 1): 
                    cv2.circle(img, (x,y), math.ceil(brushSize / 2), (int(colorPicked[0]), int(colorPicked[1]), int(colorPicked[2])), -1)
                else: img[y,x] = colorPicked

                prevX = x
                prevY = y
                painting = True
            
            # If fill tool is selected:
            elif (tool == 1):
                bucket_tool(x,y, (img[y,x,0], img[y,x,1], img[y,x,2]))

            # If box, circle, or line tool is selected:
            elif (tool > 1 and tool < 5 and y > (44 + math.ceil(brushSize / 2))):
                prevX = x
                prevY = y
                painting = True

            # If color picker is selected:
            elif (tool == 5):
                colorPicked = img[y,x]
                img[24:40, 4:196] = colorPicked
                updateSliders(colorPicked)
    
        # Color Palette @ 
        elif (y < 20 and y > 4 and x < 196 and x > 4):
            colorPicked = img[y,x]
            img[24:40, 4:196] = colorPicked
            updateSliders(colorPicked)

        # Brush Tool Button @ [4:20, 228:281]
        elif (y < 20 and y > 4 and x > 228 and x < 281):
            resetButtonText()
            tool = 0
            cv2.putText(img, "Brush", (227, 18), cv2.FONT_HERSHEY_SIMPLEX, .61, (255, 0, 0), 1)

        # Bucket Fill Tool Button @ [24:40, 228:281]
        elif (y > 24 and y < 40 and x > 228 and x < 281):
            resetButtonText()
            tool = 1
            cv2.putText(img, "Fill", (227, 38), cv2.FONT_HERSHEY_SIMPLEX, .61, (255, 0, 0), 1)

        # Box Button @ [4:20, 285:338]
        elif (y < 20 and y > 4 and x > 285 and x < 338):
            resetButtonText()
            tool = 2
            cv2.putText(img, "Box", (284, 18), cv2.FONT_HERSHEY_SIMPLEX, .61, (255, 0, 0), 1)

        # Circle Button @ [24:40, 285:338]
        elif (y < 40 and y > 24 and x > 285 and x < 338):
            resetButtonText()
            tool = 3
            cv2.putText(img, "Circle", (284, 38), cv2.FONT_HERSHEY_SIMPLEX, .61, (255, 0, 0), 1)

        # Line Button @ [4:20, 342:395]
        elif (y < 20 and y > 4 and x > 342 and x < 395):
            resetButtonText()
            tool = 4
            cv2.putText(img, "Line", (341, 18), cv2.FONT_HERSHEY_SIMPLEX, .61, (255, 0, 0), 1)

        # Color Picker Button @ [24:40, 342:395]
        elif (y < 40 and y > 24 and x > 342 and x < 395):
            resetButtonText()
            tool = 5
            cv2.putText(img, "Pick", (341, 38), cv2.FONT_HERSHEY_SIMPLEX, .61, (255, 0, 0), 1)


        # Undo Button @ [24:40, 406:455]
        elif (x > 406 and x < 455 and y > 24 and y < 40):
            print("Undo")
            img[44:,:] = saveState

        # Save Button @ [4:20, 459:508]
        elif (x > 459 and x < 508 and y > 4 and y < 20):
            saveImg = img[44:, :]
            cv2.imwrite('GoPaint_save.png', saveImg)
            print("Saved Canvas as GoPaint_save.png")

        # Clear Button @ [24:40, 459:508]
        elif (x > 459 and x < 508 and y > 24 and y < 40):
            img[44:, :] = [255,255,255]

# Resets all tool buttons to black font
def resetButtonText():
    cv2.putText(img, "Brush", (227, 18), cv2.FONT_HERSHEY_SIMPLEX, .61, (0, 0, 0), 1)
    cv2.putText(img, "Fill", (227, 38), cv2.FONT_HERSHEY_SIMPLEX, .61, (0, 0, 0), 1)
    cv2.putText(img, "Box", (284, 18), cv2.FONT_HERSHEY_SIMPLEX, .61, (0, 0, 0), 1)
    cv2.putText(img, "Circle", (284, 38), cv2.FONT_HERSHEY_SIMPLEX, .61, (0, 0, 0), 1)
    cv2.putText(img, "Line", (341, 18), cv2.FONT_HERSHEY_SIMPLEX, .61, (0, 0, 0), 1)
    cv2.putText(img, "Pick", (341, 38), cv2.FONT_HERSHEY_SIMPLEX, .61, (0, 0, 0), 1)

# Trackbar listeners
def setBlue(pos):
    setColorPicked(blue=pos)

def setGreen(pos):
    setColorPicked(green=pos)

def setRed(pos):
    setColorPicked(red=pos)

# Update single R, G, or B value of colorPicked
def setColorPicked(red=-1,green=-1,blue=-1):
    global colorPicked
    if (red == -1): red = colorPicked[2]
    else: colorPicked[2] = red
    if (green == -1): green = colorPicked[1]
    else: colorPicked[1] = green
    if (blue == -1): blue = colorPicked[0]
    else: colorPicked[0] = blue
    img[24:40, 4:196] = colorPicked

# Set sliders to currently selected color values
def updateSliders(colorPicked):
    cv2.setTrackbarPos('B', 'GoPaint', colorPicked[0])
    cv2.setTrackbarPos('G', 'GoPaint', colorPicked[1])
    cv2.setTrackbarPos('R', 'GoPaint', colorPicked[2])


### Setup

# Setting up the Window and Sliders
cv2.namedWindow('GoPaint', cv2.WINDOW_GUI_EXPANDED | cv2.WINDOW_AUTOSIZE)
cv2.createTrackbar('R', 'GoPaint', 0, 255, setRed)
cv2.createTrackbar('G', 'GoPaint', 0, 255, setGreen)
cv2.createTrackbar('B', 'GoPaint', 0, 255, setBlue)

# Initialize White 556x512 Window
img = np.zeros((556,512,3), np.uint8) + 255

# Toolbar Background
img[:44, :] = [144,144,144]

# Color Palette @ [4:20, 4:196]
img[4:20, 4:20] = [0,0,255]        #Red
img[4:20, 20:36] = [0,128,255]     #Orange
img[4:20, 36:52] = [0,255,255]     #Yellow
img[4:20, 52:68] = [0,255,0]       #LightGreen
img[4:20, 68:84] = [0,128,0]       #Green
img[4:20, 84:100] = [255,0,0]      #Blue
img[4:20, 100:116] = [255,244,96]  #LightBlue
img[4:20, 116:132] = [255,0,255]   #Pink
img[4:20, 132:148] = [128,0,96]    #Purp
img[4:20, 148:164] = [0,20,128]    #Brown
img[4:20, 164:180] = [0,0,0]       #Black
img[4:20, 180:196] = [255,255,255] #White

#Selected Color Preview
img[24:40, 4:196] = [0,0,0]


# Brush Size Readout
img[4:40, 200:224] = [180,180,180]
cv2.putText(img, "Px", (200, 18), cv2.FONT_HERSHEY_SIMPLEX, .61, (0, 0, 0), 1)
cv2.putText(img, str(brushSize), (199, 38), cv2.FONT_HERSHEY_SIMPLEX, .61, (0, 0, 0), 1)

# Brush Button
img[4:20, 228:281] = [200,200,200]
cv2.putText(img, "Brush", (227, 18), cv2.FONT_HERSHEY_SIMPLEX, .61, (255, 0, 0), 1)

# Fill Button
img[24:40, 228:281] = [200,200,200]
cv2.putText(img, "Fill", (227, 38), cv2.FONT_HERSHEY_SIMPLEX, .61, (0, 0, 0), 1)

# Box Button
img[4:20, 285:338] = [200,200,200]
cv2.putText(img, "Box", (284, 18), cv2.FONT_HERSHEY_SIMPLEX, .61, (0, 0, 0), 1)

# Circle Button
img[24:40, 285:338] = [200,200,200]
cv2.putText(img, "Circle", (284, 38), cv2.FONT_HERSHEY_SIMPLEX, .61, (0, 0, 0), 1)

# Line Button
img[4:20, 342:395] = [200,200,200]
cv2.putText(img, "Line", (341, 18), cv2.FONT_HERSHEY_SIMPLEX, .61, (0, 0, 0), 1)

# Eyedropper Button
img[24:40, 342:395] = [200,200,200]
cv2.putText(img, "Pick", (341, 38), cv2.FONT_HERSHEY_SIMPLEX, .61, (0, 0, 0), 1)

# Undo Button
img[24:40, 406:455] = [0,196,255]
cv2.putText(img, "Undo", (406, 38), cv2.FONT_HERSHEY_SIMPLEX, .61, (0, 0, 0), 1)

# Save Button
img[4:20, 459:508] = [144,255,144]
cv2.putText(img, "Save", (460, 18), cv2.FONT_HERSHEY_SIMPLEX, .61, (0, 0, 0), 1)

# Clear Button
img[24:40, 459:508] = [64,64,255]
cv2.putText(img, "Clear", (458, 38), cv2.FONT_HERSHEY_SIMPLEX, .61, (0, 0, 0), 1)


# Run Program Window until closed or esc is pressed
cv2.setMouseCallback('GoPaint',mouseDriver)
while cv2.getWindowProperty('GoPaint', 0) >= 0:
    cv2.imshow('GoPaint',img)
    if cv2.waitKey(20) & 0xFF == 27:
        break
cv2.destroyAllWindows()