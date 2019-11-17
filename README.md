# Newt
Newt is a small, C-like programming language that compiles to `nasm` assembly.
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
Newt is a simple language, similar to C. It is not hard to pick up, and once you learn it, you could use it for simple OSes and
system programs. Here I will explain the basics of the language.
## Variables
There are four variable types in Newt:
