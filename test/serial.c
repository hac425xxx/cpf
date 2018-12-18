#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h> //文件控制定义
#include <termios.h>//终端控制定义
#include <errno.h>
 
#define DEVICE "/dev/ttyS0"
 
int serial_fd = 0;
 
//打开串口并初始化设置
init_serial(void)
{
	serial_fd = open(DEVICE, O_RDWR | O_NOCTTY | O_NDELAY);
	if (serial_fd < 0) {
		perror("open");
		return -1;
	}
	
	//串口主要设置结构体termios <termios.h>
	struct termios options;
	
	/**1. tcgetattr函数用于获取与终端相关的参数。
	*参数fd为终端的文件描述符，返回的结果保存在termios结构体中
	*/
	tcgetattr(serial_fd, &options);
	/**2. 修改所获得的参数*/
	options.c_cflag |= (CLOCAL | CREAD);//设置控制模式状态，本地连接，接收使能
	options.c_cflag &= ~CSIZE;//字符长度，设置数据位之前一定要屏掉这个位
	options.c_cflag &= ~CRTSCTS;//无硬件流控
	options.c_cflag |= CS8;//8位数据长度
	options.c_cflag &= ~CSTOPB;//1位停止位
	options.c_iflag |= IGNPAR;//无奇偶检验位
	options.c_oflag = 0; //输出模式
	options.c_lflag = 0; //不激活终端模式
	cfsetospeed(&options, B115200);//设置波特率
	
	/**3. 设置新属性，TCSANOW：所有改变立即生效*/
	tcflush(serial_fd, TCIFLUSH);//溢出数据可以接收，但不读
	tcsetattr(serial_fd, TCSANOW, &options);
	
	return 0;
}
 
/**
*串口发送数据
*@fd:串口描述符
*@data:待发送数据
*@datalen:数据长度
*/
int uart_send(int fd, char *data, int datalen)
{
	int len = 0;
	len = write(fd, data, datalen);//实际写入的长度
    fsync(fd);
	if(len == datalen) {
		return len;
	} else {
		tcflush(fd, TCOFLUSH);//TCOFLUSH刷新写入的数据但不传送
		return -1;
	}
	
	return 0;
}
 
/**
*串口接收数据
*要求启动后，在pc端发送ascii文件
*/
int uart_recv(int fd, char *data, int datalen)
{
	int len=0, ret = 0;
	fd_set fs_read;
	struct timeval tv_timeout;
	
	FD_ZERO(&fs_read);
	FD_SET(fd, &fs_read);
	tv_timeout.tv_sec  = (10*20/115200+2);
	tv_timeout.tv_usec = 0;
	
    while(1){
        ret = select(fd+1, &fs_read, NULL, NULL, NULL);
        //如果返回0，代表在描述符状态改变前已超过timeout时间,错误返回-1
    
            
        if (FD_ISSET(fd, &fs_read)) {
            len = read(fd, data, datalen);
            return len;
        } else {
            perror("select");
            return -1;
        }
    }
	return 0;
}



void hexdump(const void* data, size_t size) {
	char ascii[17];
	size_t i, j;
	ascii[16] = '\0';
	for (i = 0; i < size; ++i) {
		printf("%02X ", ((unsigned char*)data)[i]);
		if (((unsigned char*)data)[i] >= ' ' && ((unsigned char*)data)[i] <= '~') {
			ascii[i % 16] = ((unsigned char*)data)[i];
		} else {
			ascii[i % 16] = '.';
		}
		if ((i+1) % 8 == 0 || i+1 == size) {
			printf(" ");
			if ((i+1) % 16 == 0) {
				printf("|  %s \n", ascii);
			} else if (i+1 == size) {
				ascii[(i+1) % 16] = '\0';
				if ((i+1) % 16 <= 8) {
					printf(" ");
				}
				for (j = (i+1) % 16; j < 16; ++j) {
					printf("   ");
				}
				printf("|  %s \n", ascii);
			}
		}
	}
    fflush(stdout);
}


int handle(unsigned char* buf, unsigned int len){
    char dst[200] = {0};
    if(!memcmp(buf, "\xaa\xbb\xcc\xdd", 4)){
        unsigned int size = 0;
        memcpy(&size, buf+4, 4);
        memcpy(dst, buf+8, size);
        uart_send(serial_fd,dst, size);
        return 1;
    }else{
        return 0;
    }
}


int main(int argc, char **argv)
{
	init_serial();
 
	char buf[100];
	printf("\n");
 	
	while(1){
		int len = uart_recv(serial_fd, buf, 100);
        hexdump(buf, len);
        if(!handle(buf, len)){
            uart_send(serial_fd,"fail", 4);
        }
        memset(buf, '\x00', 100);	
	}
	close(serial_fd);
	return 0;
}