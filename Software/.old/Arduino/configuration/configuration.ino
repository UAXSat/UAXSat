#include <Arduino.h>
#include "E220.h"
// #include <SoftwareSerial.h>

//Define the pins we need to use later to create the object
#define m0 4
#define m1 3
#define aux 2

//SoftwareSerial receiver(3,2)


void setup() {
    //start all of our UART connections
    Serial.begin(9600);
    Serial3.begin(9600); //default baud is 9600
    //receiver.begin(9600);

    //create our module
    Stream &mySerial = (Stream &)Serial3;
    E220 radioModule(&mySerial, m0, m1, aux);

    //Stream &mySerial = (Stream &)receiver;
    //E220 radioModule(&mySerial, m0, m1, aux);

    //initialise the module and check it communicates with us, else loop and keep trying
    while(!radioModule.init()){
        delay(5000);
    }
    //setting a permanent variable for the module
    radioModule.setAddress(1234,true);
    Serial.println(radioModule.getAddress());

    //setting a non-permanent variable for the module
    radioModule.setPower(Power_21,false);
    Serial.println(radioModule.getPower());

}

void loop() {

}
