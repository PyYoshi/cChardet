# cChardet
This library is high speed universal character encoding detector. - binding to libcharsetdetect

# Requires
Cython: [http://www.cython.org/](http://www.cython.org/)

uchardet-enhanced: [https://bitbucket.org/medoc/uchardet-enhanced/overview](https://bitbucket.org/medoc/uchardet-enhanced/overview)

# Install
### Build uchardet-enhanced
$cd /tmp

$hg clone https://bitbucket.org/medoc/uchardet-enhanced

$cd uchardet-enhanced/libcharsetdetect

$./configure

$make

$sudo make install

$ls -la /usr/local/lib

$ls -la /usr/local/include

### Build cChardet
$cd /tmp

$git clone git://github.com/PyYoshi/cChardet.git

$cd cChardet

$sudo pip install or easy_install -U cython. (If your os is Ubuntu, I recommend that you do "sudo apt-get install python-dev cython")

$python setup.py build

$sudo python setup.py install

# Benchmark
see tests.TestCchardetSpeed

### Sample(shift_jis):
testdata/wikipediaJa_One_Thousand_and_One_Nights_SJIS.txt

### PC Spec.:
CPU: Intel Core i7 860 2.8GHz

RAM: DDR3-1333 16GB

Platform: Windows 7 HP x64, Python 2.7.3 32-bit

### Result:
chardet: 4.009999990463257s, shift_jis

cchardet: 0.0009999275207519531s, shift_jis

# Contact
[My blog](http://blog.remu.biz)

Sorry for my poor English :)