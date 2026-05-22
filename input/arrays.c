// Array demo: declare a fixed-size array, fill it, read elements.

int main() {
    int nums[5];
    int i;

    for (i = 0; i < 5; i = i + 1) {
        nums[i] = i * 2;
    }

    printf(nums[2]);
    return 0;
}
