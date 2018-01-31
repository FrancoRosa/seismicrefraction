#define FASTADC 1

// defines for setting and clearing register bits
#ifndef cbi
#define cbi(sfr, bit) (_SFR_BYTE(sfr) &= ~_BV(bit))
#endif
#ifndef sbi
#define sbi(sfr, bit) (_SFR_BYTE(sfr) |= _BV(bit))
#endif


//ADC Channels Used X and Y for each level
int Gsrce = A0;    
int Gsink = A1;

//Output for sampling frecuency calculate
int ledPin = 13;      // select the pin for the LED

//Variables for saving data
int Vsrce = 0;  // variable to store the value coming from the sensor
int Vsink = 0;  // variable to store the value coming from the sensor

//LED output
bool State = false;

// strings
int threshold=0;
unsigned int samples=0;

String inputString = "";
String thresString = "";

bool stringComplete = false;
int t = 0;

const int buffersize=500;
int buffer[buffersize];
////////////////////////////////////////////////////////
// "...welcome" (Arduino prints wellcome, then, reads for:)
// Threashold, numberOfSamples
// When command is validated, shows "...waiting threshold"
// when samples are readed it start to send in this way:
// sample value 
//	1 	230
// 	2 	123
// 	3 	147
// ... ...
// 
// numberOfSamples 12
// repeats from begining


// 50Khz Samples = 	50 000 per sec
// 					5 000 per 100mS
// 					5 00 per 10mS



void setup()
{
	#if FASTADC // set prescale to 16
	sbi(ADCSRA,ADPS2) ;
	cbi(ADCSRA,ADPS1) ;
	cbi(ADCSRA,ADPS0) ;
	#endif
	
	int start;
	int stop;

	inputString.reserve(15);
	inputString = "";
	thresString.reserve(15);
	thresString = "";
	
	Serial.begin(115200);		//Uart comunication al 115200 baudrate
	pinMode(ledPin, OUTPUT);
	Serial.println("...yeah!");
	int i =0;
	 start = millis() ;
	 for (i = 0 ; i < buffersize ; i++) 
	 	{ buffer[i] = analogRead(Gsrce) ;
	 	  //delayMicroseconds(7);  //500muestras en 10ms 50KHz
	 	  //delayMicroseconds(27); //500muestras en 20ms 25KHz
	 	  //delayMicroseconds(86); //500muestras en 50ms  10Khz
	 	  //delayMicroseconds(186); //500muestras en 100ms  5Khz
	 	  //delay(1); //500muestras en 500ms  1Khz
	 	}
	 stop = millis() ;
	 Serial.print(stop - start) ;
	 Serial.print("ms para ") ;
	 Serial.print(buffersize) ;
	 Serial.println("muestras") ;
}
	///

void loop()
{
	//ADC readings
	//Vsrce=analogRead(Gsrce);Serial.printf("%03X ",Vsrce);
	//Vsink=analogRead(Gsink);Serial.printf("%03X\n",Vsink);
	//delay(5);
	int i;
	int ingeophone; 
	int insamples;
	int delayCor; 
	
	if (stringComplete) {
	    ingeophone = inputString[0]-48;
	    insamples = inputString[1]-48;
	    thresString = inputString.substring(2);
	    threshold = thresString.toInt();
	    threshold = threshold + 512;

	    switch(insamples)
	    {
	    	case 0: delayCor=7; break; //50Hz
	    	case 1: delayCor=186; break; //5Hz
	    	case 2: delayCor=86; break; //10Hz
	    	case 5: delayCor=27; break; //25Hz
	    	default: delayCor=0; break;
	    }

	    Serial.print("Geo "); Serial.println(ingeophone);
	    Serial.print("Sam "); Serial.println(insamples);
	    Serial.print("Thr "); Serial.println(threshold);
	    Serial.print("dly "); Serial.println(delayCor);
	    Serial.println("...");

	    while (true)
	    {
		Vsrce = analogRead(Gsrce);
		if (Vsrce>threshold) 
			{
			if(ingeophone == 1)
				{
				 Serial.println("Gsink");
				 for (i = 0 ; i < buffersize ; i++) 
		 			{ buffer[i] = analogRead(Gsink);
		 			  delayMicroseconds(delayCor);
		 			}
		 		}
			else
				{
				 Serial.println("Gsrce");
				 for (i = 0 ; i < buffersize ; i++) 
		 			{ buffer[i] = analogRead(Gsrce);
		 			  delayMicroseconds(delayCor);
		 			}
		 		}
	 		 for (i = 0 ; i < buffersize ; i++)
	 			{ 
	 				Serial.print(i);
	 				Serial.print(": ");
	 				Serial.println(buffer[i]);
	 			}
				Serial.println("...");

	 			break;

			}
	    }

	    // clear the string:
	    inputString = "";
	    stringComplete = false;
	  }

}


void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag so the main loop can
    // do something about it:
    if (inChar == '\r') {
      stringComplete = true;
    }
  }
}