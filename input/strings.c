// String demo: declare string variables, assign, pass through functions, print.

string greet(string name) {
    return name;
}

int main() {
    string s = "hello";
    string t;
    t = "world";

    printf(s);
    printf(t);
    printf("done");
    printf(greet("compiler"));

    // multi-arg printf mixing strings and ints
    int n = 5;
    printf("n is", n);

    return 0;
}
