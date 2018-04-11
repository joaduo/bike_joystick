// Copyright (C) 2018  Joaquin Duo under GPL v3
volatile unsigned long i_time = 0; //irq rising time
unsigned long li_time = 0; //last irq rising time
int pin2_irq = 0; //IRQ that matches to pin 2

void setup() {
  Serial.begin(9600);
  attachInterrupt(pin2_irq, count_rising, CHANGE);
  li_time = i_time = millis();
}

void count_rising() {
  i_time = millis();
}

void loop() {
  //change
  if(i_time != li_time){
    print_rpm('C', i_time, li_time);
    li_time = i_time;
  }
}

void print_rpm(char flag, unsigned long i_time, unsigned long li_time){
  Serial.print(flag);
  Serial.print(" ");
  Serial.print(i_time);
  Serial.print(" ");
  Serial.println(li_time);
}
