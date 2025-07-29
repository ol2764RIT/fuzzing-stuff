CXX = clang++
CC = clang
CXXFLAGS = -std=c++11 -g -fsanitize=address,fuzzer
INCLUDES = -I../../ -I../../deps/miniz
FUZZ_SRCS := $(wildcard fuzz-*.cc)
FUZZ_BINS := $(patsubst %.cc,%,$(FUZZ_SRCS))

all: miniz $(FUZZ_BINS)

miniz:
	$(CC) -c $(INCLUDES) -g ../../deps/miniz/miniz.c

$(FUZZ_BINS): %: %.cc miniz.o
	$(CXX) $(CXXFLAGS) $(INCLUDES) $< miniz.o -o $@

clean:
	rm -f $(FUZZ_BINS) *.o

t:
	./fuzz-load-exr
