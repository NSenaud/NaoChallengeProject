

void setup() {
Serial.begin(9600);
}

void loop() {
  static unsigned long i;
  unsigned long mot;
  if (Serial.available()>0)
  {
    mot = Serial.read();
    Serial.print(i );
    Serial.print(" : ");
    Serial.println(mot);
    delay(1000);
    i++;
  }
}
