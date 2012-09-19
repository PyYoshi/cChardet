#include "memory_leak.h"
#include "charsetdetect.h"
#include <iostream>
#include <fstream>
#include <string>
using namespace std;


#define BUFFER_SIZE 100*1024

void main(){
	::_CrtSetDbgFlag(_CRTDBG_ALLOC_MEM_DF | _CRTDBG_LEAK_CHECK_DF);
	csd_t csd = csd_open();
	if(csd == (csd_t)-1){
		std::cout << "csd_open faild\n";
		exit(1);
	}

	//ifstream ifs("E:\\MySourcecode\\git\\cchardet\\test\\testdata\\bg\\ISO-8859-5\\wikitop_bg_ISO-8859-5.txt");
	//ifstream ifs("E:\\MySourcecode\\git\\cchardet\\test\\testdata\\bg\\UTF-8\\wikitop_bg_UTF-8.txt");
	ifstream ifs("E:\\MySourcecode\\git\\cchardet\\test\\testdata\\cz\\ISO-8859-2\\wikitop_cz_ISO-8859-2.txt");
	if(!ifs){
		std::cerr<<"Cant open the file\n";
		exit(1);
	}

	int len;
	ifs.seekg(0,std::ios::end);
	len = ifs.tellg();
	ifs.seekg(0,std::ios::beg);
	char* buf = new char[len];
	ifs.read(buf,len);
	int result;
	const char *result_;
	std::cout<<"CLIENT SENDING More Data\n";
	result = csd_consider(csd, buf,len);
	if(result < 0){
		std::cout<<"csd_consider failed\n";
		exit(1);
	}
	result_ = csd_close(csd);
	if(result_ == NULL){
		std::cout<<"Unknown character set\n";
	}else{
		printf("%s\n", result_);
	}

	delete buf;
}