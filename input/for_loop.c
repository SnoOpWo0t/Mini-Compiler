// for-loop demo: sum integers 0..4 using a classic C-style `for`.

int main() {
    int sum = 0;
    int i;

    for (i = 0; i < 5; i = i + 1) {
        sum = sum + i;
    }

    printf(sum);
    return 0;
}
