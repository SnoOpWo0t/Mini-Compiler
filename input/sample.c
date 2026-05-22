// Sample program for the mini C compiler.
// Exercises basic types, arithmetic, if / else, and while.

int main() {
    int x = 5;
    int y = x + 10;

    if (y > 10) {
        printf(1);
    } else {
        printf(0);
    }

    int i = 0;
    while (i < 3) {
        printf(i);
        i = i + 1;
    }

    return 0;
}
