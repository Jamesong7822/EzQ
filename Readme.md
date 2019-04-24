# EzQ

------

## [IMPORTANT] Disclaimer

The following systems must be ran in a <b>`linux`</b> based environment (in our case: `ubuntu`) in order to run the entirety of the project.

However, all other scripts (except `server.py`) can be ran in a `windows` environment.

## Pre-requisites 

The following pre-requisites are presumed to be pre-installed in your testing environment.

- `libdw`
- `kivy`
- `numpy`

## Additional Requirements

- `opencv-python`: Image processing library
- `cython`: `Cython`library
- `twilio`: `Twilio` library for messaging service
- `yolo34py`: Image - Object detection library for detection service

1. To install the libraries in this section, go into terminal/cmd prompt and navigate to the directory: `~/EzQ/EzQ`. 

2. You should see our project files:

   1. `cashier.py`, `cashier.kv`, `chefgui.py`, `chefgui.kv`, `credentials.txt`, `customer.py`, `customer.kv`, `ezq.py`,`firebase.py`, `messenger.py`,`server.py`,`twilio_credentials.txt`,
   2. Folders: 
      - `Legacy`: This folder contains all our legacy code, which are our developmental code.
      - `YOLO3-4-Py`: Image-Object detection library.

3. Type the following to install `opencv-python` and `cython`.

   ```terminal
   pip3 install -r requirements.txt
   ```

   This line installs the above mentioned libraries (specified in `requirements.txt`) into the python libraries.

4. You can skip this step, if you do not want to run `server.py`.

   To install `Yolo34py`, navigate to the folder `YOLO3-4-Py` by typing the following. This assumes that you are currently in the directory: `~/EzQ/EzQ`

   ```terminal
   cd YOLO3-4-Py/
   ```

   Next, run the following:

   ```terminal
   pip3 install .
   ```

   Ensure no errors occur. If there are errors: troubleshoot [here](https://github.com/madhawav/YOLO3-4-Py).

5. Great! Now, you are all setup to run our scripts!

## Scripting

This section will introduce in greater detail about our scripts as well as the running order.

1. `ezq.py`: Script takes an image from a web-cam and uploads it to `firebase`. 

   > **Important**
   >
   > Since the web-cam is not passed over, we offered a testing method that can be passed to the script as a form of testing for `server.py`
   >
   > To run this testing method: 
   >
   > (assuming in `/EzQ/EzQ/`directory)
   >
   > ```terminal
   > python3 ezq.py --test
   > ```
   >
   > This testing method sends over a test image (within the directory) over to `firebase`, which the script `server.py`can be ran to run the detection model on the test image.

2. `messenger.py`: Script is ran in the background to provide messaging service

   > Run it with 
   >
   > ```terminal
   > python3 messenger.py
   > ```

3. The following scripts must be ran separately but within the same step, before any inputs can be made (since they are `gui-s`). I**n short, they must be running prior to any inputs made.** 

4. - `customer.py`: `Front-end GUI`for Customers to input their hand-phone number
   - `cashier.py`: `Cashier side GUI` for Cashier to submit orders and tag it with phone number inputs from `customer.py`
   - `chefgui.py`: `Chef side GUI` for chef to update completed orders, which triggers `messenger.py`to prompt relevant customers through `Whatsapp`.
   - `server.py`: `Cloud based or Local Computer based Backend`for running of the detection module to identify number of people in queue.

