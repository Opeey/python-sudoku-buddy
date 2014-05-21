CC = gcc
CFLAGS = -Wall -lm

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $^

all: simulatedAnnealing

simulatedAnnealing: simulatedAnnealing.o
	$(CC) $(CFLAGS) -o ./$@ $< $(LDFLAGS)

clean:
	-rm *.o
	-rm ./simulatedAnnealing
