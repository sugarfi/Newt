# Newt
Newt is a small, C-like programming language that compiles to `nasm` assembly.
# Dependencies
Newt has a few dependencies:

- `python3`
- `nasm` or `yasm`
- `ld`

# Setting Up Newt
First, you must clone this repository.  
`$ git clone https://github.com/sugarfi/Newt.git`  
You will have a new directory `Newt/`.  
`cd` into it.  
`$ cd Newt/`  
*Linux users only*
To make Newt easier to run, make the `newt.py` file executable.  
`$ chmod +x newt.py`  
Now you can run `python3 newt.py yourfile.newt`, or, if you followed the previous step,`./newt.py yourfile.newt`.
# Compiling and Running
Once you have Newt set up on your system, you are ready to compile and run code.  
First, run `newt.py` on you file.  
`$ ./newt.py yourfile.newt`  
You will not have a `yourfile.asm` file. To run it, you must assemble it with `nasm` or `yasm`.  
`$ nasm -felf -o yourfile.o yourfile.asm`  
Now we must use `ld` to compile the file to an executable.  
`$ ld -o yourfile yourfile.o`  
Finally, we can run the code.  
`$ ./yourfile`  
# Tutorial
Newt is a simple language, similar to C. It is not hard to pick up, and once you learn it, you could use it for simple OSes 
and system programs. Here I will explain the basics of the language.
## Comments
Comments are defined, as in Python, with a `#`. For example:
```
# This is a comment on its own line
byte abc = 123; # This is a comment after a line.
```
## Variables
There are four variable types in Newt: `byte`, `word`, `dword`, and `qword`. A byte, as you know, is 8 bits. A word is 2 
bytes,
or 16 bits. A dword is 2 words, or 32 bits. A qword is 4 words, or 64 bits. Note that Newt is statically typed: you cannot,
or at least should not, assign two different types to a variable. Here is how you would assign to a variable:
```
byte a = 5;
dword b = 5;
word c = 5;
c = 6;
byte a = 7;
```
Note that when you reassign a variable, you may or may not specify its type.
### Strings
The `byte` type in Newt has a special feature: you can use it for strings. This is useful if you need to print text, or store user input. Strings are defined using double quotes, like this:
```
byte hello = "hello world!";
```
Note that when using `mov` to copy strings into a register, you must use inline assembly to get the string's address, not 
its first character. You would end up with something like this:
```
byte hello = "hello";
asm {
mov ebx, hello
}
```
## Function Calls
There are two types of function calls in Newt: defined functions and assembly functions. Before we get to that, though,
function calls are made like this:
```
print(a);
add(5, 6);
```
If a function has been defined previously in your code, it will be called. Otherwise, the compiler will treat it as an
assembly instruction. This might be better understood with an example. Assume you have a function `hello`, but not one 
called `mov`. The following code:
```
hello(5);
mov(eax, 5);
```
Would compile to:
```
mov [arg], 5
call hello
mov eax, 5
```
Note that user-defined functions cannot have retun values. They must store their output in a variable. Also note that, since
arguments to user-defined functions are considered variables, they are defined as such. Thus, the following code:
```
add(1, 2);
```
Is equivalent to:
```
byte arg1 = 1;
byte arg2 = 2;
add();
```
## Conditionals and Loops
The only conditional structure is the if statement. If statements are of the form:
```
if (a == b) {
  c(a, b);
}
```
You cannot do things like `if(1) {print("ok")}`, since if statements must always have two values and an operator.
There are no else-clauses, so to implement if statements with multiple choices, you would do something like:
```
if (a == b) {
  func_a(a, b);
}
if (a != b) {
  func_b(a, b)
}
```
Loops are a little bit more versatile. The simplest loop in Newt is the while loop. While loops are similar to if
statements:
```
while (a > b) {
  my_func(a);
}
```
Again, you cannot do things like `while (1) { function(1); }`. However, you could do:
```
while (1 == 1) {
  update(stuff);
}
```
For loops are simple, too. They always use a variable as a counter, and go from a minimum to a maximum. They are expressed like this:
```
for (i, 0, 4) {
  code(i);
}
```
`i` will be automatically incremented. The above code is bascially equivalent to:
```
i = 0;
while (i < 4) {
  code(i);
  asm {
    inc [i];
  }
}
```
## Defining Functions
Function definitions are done with the `define` keyword. For example, to define a function `abc` that takes 3 arguments, you 
would do:
```
define abc(byte a, word b, dword c) {
  ...
}
```
You could then call `abc(1, 2, 3);` or something similar. There are some constraints, however. For one thing, functions 
cannot have a return value. You would have to store output in a variable, like `_`. Another is that you cannot call a 
function without arguments. The compiler will throw an error. However, you probably would not use functions without
arguments much, so this is ok.
## Other Statements
There are two other statements in Newt: `asm` and `goto`. `asm` is used for inline assembly. Anything inside an `asm` block 
is written directly to the output file, without being modified at all. Thus, the following:
```
mov(eax, 5);
```
Is the same as:
```
asm {
  mov eax, 5
}
```
This might seem useless, but it does have some applications. For one, in a simple bootsector, you would use this to take 
advantage of BIOS interrupts. As well, when printing strings, this is needed. The reason is that Newt compiles `mov(a, 5);` 
to `mov [a], 5`, for example, because variables are stored using `nasm`'s `db`, `dw`, `dd`, and `dq`, which set a variable 
to the address of its value. It is like pointers in C. To get a pointer's value, you must dereference it first.
However, most string functions require you to use the address of the string. To get around this, use `asm`:
```
asm {
  mov ebx, a
}
```
The `goto` statement is more simple. It does not get compiled to anything on its own; it simply sends the compiler to the 
line it was given. Lines are 0-indexed. For example, you would do:
```
goto 0;
```
To jump to the first line. You could also do:
```
byte a = 0;
goto a;
```
## The Preprocessor
Newt also comes with a preprocessor, like in C. This can be used for including other files, for example. Preprocessor 
instructions take the format:
```
@include file.newt;
@define abc 123;
```
Note the semicolons!
### Preprocessor Macros

- The `@include` includes another file in this one. Note that, for large files, this will directly insert the contents
  of the file. For example, if you have a file `abc.newt`:
  ```
  define abc(byte a) {
    a = 123;
  }
  ```
  Then this:
  ```
  @include abc.newt;
  byte c = 5;
  abc(c);
  ```
  Would be run as:
  ```
  define abc(byte a) {
    a = 123;
  }
  byte c = 5;
  abc(c);
  ```
- The `@define` macro defines a preprocessor variable and replaces all occurrences of it in the code. This one is pretty
  simple. This code:
  ```
  @define hello "hello";
  print(hello);
  ```
  Would be evaluated as:
  ```
  print("hello");
  ```
  Beware of single letter variables! Using something like `@define a 5;` would replace **every** `a` in your code with a 5.
## Notes
A couple of things before you start developing:

- There are still some features I plan on adding to Newt. It is not complete yet.
- Variables are defined using the `db` and friends `nasm` statements, which set the variable to the address of their value.
  Therefore, if you want modify a variable using an `asm` block, you would have to use brackets around its name, like
  this:
  ```
  byte a = 5;
  asm {
    mov byte [a], 6
  }
  ```
- While Newt does not support pointers yet (curse you, segfaults!), you can implement them in assembly. You would just do 
  something like (I believe):
  ```
  byte a = 0;
  asm {
    mov al, [0x7897]
    mov [a], al
  }
  ```
- Newt does not have its own built-in errors. Any errors you get at compile time are from Python.
  Here is a brief explanation:
  
  - The compiler hangs forever. You had a syntax error. The lexer will continue running till it finds a match for a line,
    so if none is found, it hangs.
  - `KeyError: None` means that the parser was not able to parse your lexed code. Runner functions are stored in a 
    dictionary. The parser returns `None` on failure. The compiler does not know this, and will attempt to use 
    `None` as a key.
  - Pretty much anything else means that a runner function failed, and that my code has a problem. Report the full error as 
    an issue.
# Credits and License
Newt was an idea I had a while ago, but it was inspired by [the U programming language](https://github.com/upcrob/u-programming-language).  
I don't really care how or what you use this software for. It is totally free. However, credit would be nice.  
Newt was developed with Python 3, `nasm`, and the Internet.

---
