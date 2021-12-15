# The Computer Language Benchmarks Game
# https://salsa.debian.org/benchmarksgame-team/benchmarksgame/
# contributed by Joerg Baumann
# Modified for benchmarking by Pawel A. Hernik

# Results:
# Intel i3-4130T   Win8     43.91/24.19
# Intel i7-7700HQ  Debian9  31.23/ 9.23
# Ryzen 4500U      Win10    32.83/ 6.62
# Ryzen 3500U      Win11    40.42/10.49        
# Apple M1 (MBA)   macOS    18.78/ 3.84
# Apple M1 Pro     macOS

from contextlib import closing
from itertools import islice
from os import cpu_count
from sys import argv, stdout
import time

def pixels(y, n, abs):
    range7 = bytearray(range(7))
    pixel_bits = bytearray(128 >> pos for pos in range(8))
    c1 = 2. / float(n)
    c0 = -1.5 + 1j * y * c1 - 1j
    x = 0
    while True:
        pixel = 0
        c = x * c1 + c0
        for pixel_bit in pixel_bits:
            z = c
            for _ in range7:
                for _ in range7:
                    z = z * z + c
                if abs(z) >= 2.: break
            else:
                pixel += pixel_bit
            c += c1
        yield pixel
        x += 8

def compute_row(p):
    y, n = p

    result = bytearray(islice(pixels(y, n, abs), (n + 7) // 8))
    result[-1] &= 0xff << (8 - n % 8)
    return y, result

def ordered_rows(rows, n):
    order = [None] * n
    i = 0
    j = n
    while i < len(order):
        if j > 0:
            row = next(rows)
            order[row[0]] = row
            j -= 1

        if order[i]:
            yield order[i]
            order[i] = None
            i += 1

def compute_rows(n, f, m):
    row_jobs = ((y, n) for y in range(n))

    #if cpu_count() < 2:
    if m < 1:
        yield from map(f, row_jobs)
    else:
        from multiprocessing import Pool
        with Pool() as pool:
            unordered_rows = pool.imap_unordered(f, row_jobs)
            yield from ordered_rows(unordered_rows, n)

def mandelbrot(m):
    n = 4000
    f = open("mandelbrot.pbm", "wb")
    wr = f.write
    print("Size:      ",n)
    print("CpuCount:  ",cpu_count())
    start = time.time()

    with closing(compute_rows(n, compute_row, m)) as rows:
        wr("P4\n{0} {0}\n".format(n).encode())
        for row in rows:
            wr(row[1])
    f.close()

    end = time.time()
    print("== Elapsed time: %.2f" % (end - start))
    print();

if __name__ == '__main__':
    print('--- Single ---')
    mandelbrot(0)
    print('--- Multi ---')
    mandelbrot(1)
