// Semantic error demo: redeclaration, undeclared, type mismatch, bad return.

int main() {
    int x = 10;
    int x = 20;          // redeclaration of 'x'

    y = x + 1;           // undeclared identifier 'y'

    float f = 2.5;
    int z = f;           // type mismatch: float -> int

    return 0;
}

void do_nothing() {
    return 7;            // void function returns a value
}
