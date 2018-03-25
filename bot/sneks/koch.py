from PIL import Image,ImageDraw
import os
from typing import Tuple
import io


SNAKE_IMG = "snake.png"
SNAKE_THUMBNAIL_SIZE = 16,16
SNAKE_THUMBNAIL_IMG = "snake_thumbnail.png"

if SNAKE_THUMBNAIL_IMG not in os.listdir(os.path.dirname(__file__)):
    snake_img = Image.open(os.path.dirname(__file__) + "/" + SNAKE_IMG)
    snake_img.thumbnail(SNAKE_THUMBNAIL_SIZE,Image.ANTIALIAS)
    snake_img.save("snake_thumbnail.png")

SNAKE_ICON = Image.open(os.path.dirname(__file__) + "/" + SNAKE_THUMBNAIL_IMG)

class SnakeSierpinksiFractal():
    def __init__(self):
        self.img = Image.new("RGB",(2400,2400),"white")
        self.draw = ImageDraw.Draw(self.img)


    def sierpinski(self,data:Tuple, steps:int, update_image, k:int):
        '''
        calculates points for sub triangles, uses recursion for steps
        '''
        # draw triangles each step through
        points = []
        update_image.line((data[0], data[1]))
        update_image.line((data[1], data[2]))
        update_image.line((data[0], data[2]))
        points.append(( int(data[0][0]), int(data[0][1])))

        # next triangle formed by connecting the midpoints of each of the sides
        x1 = (data[0][0] + data[1][0]) / 2
        y1 = (data[0][1] + data[1][1]) / 2

        x2 = (data[1][0] + data[2][0]) / 2
        y2 = (data[1][1] + data[2][1]) / 2

        x3 = (data[2][0] + data[0][0]) / 2
        y3 = (data[2][1] + data[0][1]) / 2

        # updates data in next recursion
        data2 = ((x1, y1), (x2, y2), (x3, y3))

        # loop through until step limit is reached
        k += 1
        if k <= steps:
            # the functions calls itself (recursion)
            return (self.sierpinski((data[0], data2[0], data2[2]), steps, update_image, k) +
                    self.sierpinski((data[1], data2[0], data2[1]), steps, update_image, k) +
                    self.sierpinski((data[2], data2[1], data2[2]), steps, update_image, k))
        else:
            return points


    def create_image(self,id:str,steps:int=6):
        data = ((0, 500), (500, 500), (250, 0))
        size = data[1]
        picture = Image.new('1', size, color="white")
        update_image = ImageDraw.Draw(picture)

        points = self.sierpinski(data, steps, update_image, 0)

        for point in points:
            picture.paste(SNAKE_ICON,(point[0],point[1]))

        image_name = "snake{}.png".format(id)
        stream = io.BytesIO()
        picture.save(stream,format="JPEG")
        picture_file = stream.getvalue()

        return picture_file