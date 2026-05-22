// Function demo: declaration, parameter passing, recursion, return values.

int add(int a, int b) {
    return a + b;
}

int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int main() {
    int x = add(3, 4);          // simple call
    int f = factorial(5);       // recursion
    printf(x, f);
    return 0;
}
