# mobile-test
This repository contains the program that allows running an appium test on real device using the blazemeter platform

# How to run the mobile tester script
Download this repository. Assuming you have python 2.x environment, you can run the script ```python mobile-tester.py --help``` to see all the options

You can install the required files using pip.

You will need a blazemeter api keys to run the program. You can get one by signing up for free account at blazemeter.com


# Getting started
Assuming is that you have a working python 2.x environment. 
1. Download the repository
2. Go to the root directory
3. Type in ```pip install -r requirements.txt```
4. Type ```python mobile-tester.py``` and follow the prompts
5. Alternatively type ```python mobile-tester.py --api_key=<YOUR_API_KEY_HERE> --api_secret=<YOUR_API_SECRET_HERE> --name MobileTest``` and follow the prompts to run the bundled test on blazemeter platform


# Adding your mobile app
You can add your mobile app that you want to test in the resources directory. The bundled mobile app ipa is using the source code from this repository https://github.com/Blazemeter/blazedemo-ios-app

# Adding your appium tests

You can add your test under the test-files/python/tests directory. Ideally you can replace the existing blaze_demo_test.py script. Make sure you add your additional requirements for your appium test in the requirements.txt file under the test-files/python directory. 

Ideally since we are running this test on a real device that is pointing to your application, the only configuration you need to pass into desired capabilites would be the bundle id

```
 self.driver = webdriver.Remote(
        command_executor='http://127.0.0.1:4723/wd/hub',
        desired_capabilities={
            'bundleId': 'CA.BlazeDemo',
        })
```

You can then bundle the tests by zipping them using the create_bundle script provided in the python directory. 

```
./create_bundle.sh 
```

This zipped artifact is what blazemeter uses to upload and run the tests. 