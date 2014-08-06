/* Name: main.c
 * Project: Handschuh Controller - die Firmware für den Handschuh
 * Author: Nils Braun
 */

/*
 * Dies ist die Firmware für den Mikrocontroller. Sie steuert die
 * Kommunikation über USB und die AD-Wandlung. Nach der Initialisierung der Schnittstellen
 * wird in einem Zeitschritt der momentane Status der Sensoren abgefragt und dann
 * in den Puffer geschrieben. Werden die Daten vom USB-Host abgefragt, wird dieser Puffer gesendet.
 */


#include <avr/io.h>
#include <avr/wdt.h>

#include "usb.h"
#include "TWI.h"
#include "usbdrv/usbdrv.h"

uint8_t flag = 0;

int main(void)
{
	// Watchdog auf 1 Sekunde setzen, um bei einem Fehler sofort neuzustarten
	wdt_enable(WDTO_1S);

	// USB initialisieren, Ports setzen
	usbInit();
	
	// TWI initialisieren
	twiInit();

	// Reenumeration forsieren
	usbForceDisconnect();

	// I2C initialisieren
	// PC0, PC1: Eingänge mit Pullup = DATEN
	DDRC = 0;
	PORTC = (1 << 0) | (1 << 1);
	
	// VCC-Versorgung für die LED
	DDRB = 0xFF;
	PORTB = (1 << 0);
			
	// USB: Nachrichtenschleife ausführen, watchdog zurücksetzen, USB-Nachrichten abrufen,
	// I2C-Nachrichten abrufen
	while(1)
	{
		wdt_reset();

		// Auf Nachricht warten
		usbPoll();
		twiPoll();
	}

	return 0;
}