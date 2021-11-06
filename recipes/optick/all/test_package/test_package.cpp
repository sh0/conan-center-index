#include <cstdlib>
#include <optick.h>

int main() {
    OPTICK_THREAD("MainThread");
    OPTICK_FRAME("Main");
    return EXIT_SUCCESS;
}
