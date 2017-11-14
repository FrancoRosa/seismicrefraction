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

void setup()
{
	Serial.begin(115200);		//Uart comunication al 115200 baudrate
	pinMode(ledPin, OUTPUT);
}

void loop()
{
	//ADC readings
	Vsrce=analogRead(Gsrce);Serial.printf("%03X ",Vsrce);
	Vsink=analogRead(Gsink);Serial.printf("%03X\n",Vsink);
	delayMicroseconds(550);
	State = !State;
	digitalWrite(ledPin, State);
}

