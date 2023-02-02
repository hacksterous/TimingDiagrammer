# TimingDiagrammer
## An application to draw timing diagrams for digital logic.

This is a successor to the [waves](https://github.com/hacksterous/waves) app that I wrote a long time ago.
It was simple, but lacked a few features like saving entire canvas (not just the viewport) as an image (which
seemed hard to implement in Tk. Also, waves had a few glaring omissions like not supporting the ':' in the 
signal name and ability to color data.

I have tried to fix these in Timing Diagrammer, which is written using PyQt5.

## Running on GNU/Linux:

Install PyQT5

```
$ pip3 install pyqt5
```

Run the Python source:
```
$ cd TimingDiagrammer/
$ python3 TimingDiagrammer.py
```

## Running on Windows:
Timing Diagrammer can be run from the source like above, or run from the binary in releases/ directory.

## A more complex example
![example](https://user-images.githubusercontent.com/16697108/212528785-ff1b2a6d-5e8c-4f9a-8874-f87a3ef44130.jpg)

Here is a video of Timing Diagrammer being used to draw a simple timing diagram -- 

![Animation](https://user-images.githubusercontent.com/16697108/216374652-d593b8e5-1e76-49cf-889d-c9ec917e5616.gif)

The usual disclaimer applies.

###    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
