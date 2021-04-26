import cv2
import numpy as np


# Trackbars: Create the trackbars for adjusting the marker colors.
def empty(x):
    pass
cv2.namedWindow("Marker Detector")
cv2.createTrackbar("Hue Max", "Marker Detector", 71, 180, empty)
cv2.createTrackbar("Sat Max", "Marker Detector", 255, 255, empty)
cv2.createTrackbar("Val Max", "Marker Detector", 255, 255, empty)
cv2.createTrackbar("Hue Min", "Marker Detector", 57, 180, empty)
cv2.createTrackbar("Sat Min", "Marker Detector", 107, 255, empty)
cv2.createTrackbar("Val Min", "Marker Detector", 0, 255, empty)


# Mask: Create mask to show the marker depends in the values of te trackbars.
def mask(img):
    global colorID, size
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h_max = cv2.getTrackbarPos("Hue Max", "Marker Detector")
    s_max = cv2.getTrackbarPos("Sat Max", "Marker Detector")
    v_max = cv2.getTrackbarPos("Val Max", "Marker Detector")
    h_min = cv2.getTrackbarPos("Hue Min", "Marker Detector")
    s_min = cv2.getTrackbarPos("Sat Min", "Marker Detector")
    v_min = cv2.getTrackbarPos("Val Min", "Marker Detector")
    Upper_hsv = np.array([h_max, s_max, v_max])
    Lower_hsv = np.array([h_min, s_min, v_min])
    kernel = np.ones((5, 5), np.uint8)

    mask = cv2.inRange(imgHSV, Lower_hsv, Upper_hsv)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.dilate(mask, kernel, iterations=1)
    cv2.imshow("Marker", mask)

    # Send the mask to getContours to get the center point of the marker.
    x, y = getContours(mask)

    # Draw the circle on the marker if it's detected.
    # The circle center is the center of the contour, color and size of the selected brush.
    if x & y != -1:
        cv2.circle(imgResult, (x, y), size, colors[colorID], cv2.FILLED)

    return x, y


# GetContours: Detect the contours from mask image and return the center point of the marker.
def getContours(img):
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if len(contours) > 0:
        cnt = sorted(contours, key=cv2.contourArea, reverse=True)[0]
        ((x, y), radius) = cv2.minEnclosingCircle(cnt)

        # The center point
        M = cv2.moments(cnt)
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

    # Not detected marker return -1
    else:
        cx, cy = -1, -1

    return cx, cy


# Buttons: Create buttons for toolbar to show them on each frame
def buttons():
    # Colors
    cv2.circle(imgResult, (color_circleX, color_circleY), color_corcleR, colors[0], cv2.FILLED)  # Blue
    cv2.circle(imgResult, (2 * color_circleX, color_circleY), color_corcleR, colors[1], cv2.FILLED)  # Green
    cv2.circle(imgResult, (3 * color_circleX, color_circleY), color_corcleR, colors[2], cv2.FILLED)  # Red
    cv2.circle(imgResult, (4 * color_circleX, color_circleY), color_corcleR, colors[3], cv2.FILLED)  # Yellow

    # Size
    cv2.circle(imgResult, ((frameWidth // 2 - color_circleX), color_circleY), font_size, colors[colorID],
               cv2.FILLED)  # Small
    cv2.circle(imgResult, (frameWidth // 2, color_circleY), font_size * 2, colors[colorID], cv2.FILLED)  # Medium
    cv2.circle(imgResult, ((frameWidth // 2 + color_circleX), color_circleY), font_size * 3, colors[colorID],
               cv2.FILLED)  # Large

    # Save
    cv2.circle(imgResult, ((frameWidth - 5 * color_circleX), color_circleY), color_corcleR * 2, colors[4], cv2.FILLED)
    cv2.putText(imgResult, "Save",
                ((frameWidth - 5 * color_circleX) - int(1.7 * color_corcleR), color_circleY + color_corcleR // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    # Eraser
    cv2.circle(imgResult, ((frameWidth - 3 * color_circleX), color_circleY), color_corcleR * 2, colors[5], cv2.FILLED)
    cv2.putText(imgResult, "Eraser",
                ((frameWidth - 3 * color_circleX) - int(1.6 * color_corcleR), color_circleY + color_corcleR // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)

    # Clear
    cv2.circle(imgResult, ((frameWidth - color_circleX), color_circleY), color_corcleR * 2, colors[6], cv2.FILLED)
    cv2.putText(imgResult, "Clear",
                ((frameWidth - color_circleX) - int(1.8 * color_corcleR), color_circleY + color_corcleR // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)


# Toolbar
# Create toolbar to control brush color, size, and buttons
def toolbar(x, y):
    global colorID, size, eraser_flag

    # Color Section
    if 0 < x <= 5 * color_circleX:
        eraser_flag = False  # Deactivate the eraser to draw.

        if color_circleX < x < color_circleX + color_corcleR:
            colorID = 0  # Blue
        elif (2 * color_circleX) <= x <= (2 * color_circleX) + (color_corcleR):
            colorID = 1  # Green
        elif (3 * color_circleX) <= x <= (3 * color_circleX) + (color_corcleR):
            colorID = 2  # Red
        elif (4 * color_circleX) <= x <= (4 * color_circleX) + (color_corcleR):
            colorID = 3  # Yellow

    # Size Section
    elif (frameWidth // 2 - color_circleX) <= x <= (frameWidth // 2 - color_circleX) + (2 * font_size):
        size = font_size  # Small
    elif (frameWidth // 2) <= x <= (frameWidth // 2) + (4 * font_size):
        size = font_size * 2  # Medium
    elif (frameWidth // 2 + color_circleX) <= x <= (frameWidth // 2 + color_circleX) + (6 * font_size):
        size = font_size * 3  # Large

    # Buttons
    elif (frameWidth - 5 * color_circleX) - (2 * color_corcleR) <= x <= (frameWidth - 5 * color_circleX):
        saveSketch()  # Save
    elif (frameWidth - 3 * color_circleX) - (2 * color_corcleR) <= x <= (frameWidth - 3 * color_circleX):
        eraser_flag = True  # Eraser
    elif (frameWidth - color_circleX) - (2 * color_corcleR) <= x <= (frameWidth - color_circleX):
        clear()  # Clear

    return colorID, size


# Draw: Draw lines on imgResult and sketch
def drawOnCanvas(x, y):
    global xp, yp, imgResult

    # If the previous point (xp, yp) = 0, the previous point will equal the current point to draw separate lines.
    if xp & yp == 0:
        xp, yp = x, y

    cv2.line(imgResult, (xp, yp), (x, y), colors[colorID], size)
    cv2.line(sketch, (xp, yp), (x, y), colors[colorID], size)

    # Update the precious point with the current point for the next point to draw connected lines.
    xp, yp = x, y


# Save: Save the sketch in the jpg image.
def saveSketch():
    global i, clean

    # Check if the sketch is not clean before saving for not duplicating the the same image.
    if not clean:
        i += 1
        sketch_path = f"sketch-{i}.jpg"
        cv2.imwrite(sketch_path, sketch)

    # Clear the sketch to create a new one and update clean value.
    clear()


# Eraser: Erase the draw by drawing om it with the same color of the sketch background color.
def eraser(x, y):
    global colorID, size
    colorID = 5
    cv2.circle(sketch, (x, y), color_corcleR, (0, 0, 0), size)


# Clear: Clear all draw on the sketch.
def clear():
    global sketch, clean
    sketch = np.zeros((frameHeight, frameWidth, 3), np.uint8)

    # Update the clean value for save function.
    clean = True


# Show: Mask the draw from the sketch on imgResult.
def show():
    global imgResult, sketch
    imgGray = cv2.cvtColor(sketch, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    imgResult = cv2.bitwise_and(imgResult, imgInv)
    imgResult = cv2.bitwise_or(imgResult, sketch)


# Video Properties
frameWidth = 640
frameHeight = 480
# cap = cv2.VideoCapture(0)   # Default Camera
cap = cv2.VideoCapture(1)  # Secondary Camera
# cap = cv2.VideoCapture("http://192.168.1.3:8080/video") # IP Camera
cap.set(3, frameWidth)
cap.set(4, frameHeight)
cap.set(10, 150)


# Colors of brushes
#           Blue         Green           Red           Yellow           Save           Brush          Clear
colors = [(221, 82, 6), (55, 209, 76), (39, 32, 234), (36, 202, 249), (146, 153, 7), (46, 39, 30), (24, 65, 232)]
colorID = 2

# Font_size * (1,2,3) and the current size.
font_size = 5
size = 5

# The center and radius of brushes.
color_circleX = 40
color_corcleR = 12
color_circleY = 20 + color_corcleR

# The initial prevoius points.
xp, yp = 0, 0

# The initial iterator.
i = 0

# Eraser flag to activate and deactivate the eraser.
eraser_flag = False

#
sketch = np.zeros((frameHeight, frameWidth, 3), np.uint8)


# Main
while True:
    sucess, img = cap.read()
    img = cv2.flip(img, 1)
    imgResult = img.copy()

    buttons()  # Display buttons.

    x, y = mask(imgResult)  # Get the center point.

    show()  # Display the old draw.

    if x & y == -1:  # Reset xp and yp when not detected contour.
        xp, yp = 0, 0

    elif 0 < y <= color_circleY * 2:  # Access Toolbar
        colorID, size = toolbar(x, y)

    elif eraser_flag:
        eraser(x, y)  # Use Eraser

    else:  # Draw the new lines.
        drawOnCanvas(x, y)
        clean = False

    cv2.imshow("Result", imgResult)
    cv2.imshow("Sketch", sketch)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break