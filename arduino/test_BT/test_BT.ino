


void setup() 
{
  Serial.begin(9600); // initialisation du débit série à 9600bauds/s
}

void loop() 
{
  unsigned short codeBT;
  if (Serial.available() > 0)  //enclenchement par Bluetooth
  {
    codeBT = Serial.read();
    Serial.println("Information detectee suivante :");
    Serial.println(codeBT);
    
  }
  delay(100);

}
