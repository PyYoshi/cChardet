# cChardet
This library is high speed universal character encoding detector. - binding to libcharsetdetect

# Requires
Cython: [http://www.cython.org/](http://www.cython.org/)

uchardet-enhanced: [https://bitbucket.org/medoc/uchardet-enhanced/overview](https://bitbucket.org/medoc/uchardet-enhanced/overview)

pip install or easy_install -U cython

# Benchmark
see tests.TestCchardetSpeed

Sample(shift_jis): testdata/wikipediaJa_One_Thousand_and_One_Nights.txt

## Result

chardet: 4.009999990463257s, shift_jis

cchardet: 0.0009999275207519531s shift_jis

# Contact
[My blog](http://blog.remu.biz)

Sorry for my poor English :)