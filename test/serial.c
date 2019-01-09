// gcc test.c -o test -w
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <termios.h>
#include <time.h>
#include <stdlib.h>

#define FALSE -1
#define TRUE 0

void set_speed(int, int);
int set_Parity(int, int, int, int);

void hexdump(const void *data, size_t size)
{
    char ascii[17];
    size_t i, j;
    ascii[16] = '\0';
    for (i = 0; i < size; ++i)
    {
        printf("%02X ", ((unsigned char *)data)[i]);
        if (((unsigned char *)data)[i] >= ' ' && ((unsigned char *)data)[i] <= '~')
        {
            ascii[i % 16] = ((unsigned char *)data)[i];
        }
        else
        {
            ascii[i % 16] = '.';
        }
        if ((i + 1) % 8 == 0 || i + 1 == size)
        {
            printf(" ");
            if ((i + 1) % 16 == 0)
            {
                printf("|  %s \n", ascii);
            }
            else if (i + 1 == size)
            {
                ascii[(i + 1) % 16] = '\0';
                if ((i + 1) % 16 <= 8)
                {
                    printf(" ");
                }
                for (j = (i + 1) % 16; j < 16; ++j)
                {
                    printf("   ");
                }
                printf("|  %s \n", ascii);
            }
        }
    }
    fflush(stdout);
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
    len = write(fd, data, datalen); //实际写入的长度
    fsync(fd);
    fdatasync(fd);
    if (len == datalen)
    {
        hexdump(data, datalen);
        return len;
    }
    else
    {
        tcflush(fd, TCOFLUSH); //TCOFLUSH刷新写入的数据但不传送
        return -1;
    }

    return 0;
}

int handle(int fd, unsigned char *buf, unsigned int len)
{
    puts("Recv");
    fflush(stdout);
    hexdump(buf, len);

    char dst[200] = {0};
    if (!memcmp(buf, "\xaa\xbb\xcc\xdd", 4))
    {
        unsigned int size = 0;
        memcpy(&size, buf + 4, 4);
        memcpy(dst, buf + 8, size);
        puts("Send");
        fflush(stdout);

        if (uart_send(fd, dst, size) <= 0)
        {
            puts("some things error!!!");
            hexdump(dst, size);
            puts("********************************");
            fflush(stdout);
        }
        return 1;
    }
    else
    {
        return 0;
    }
}

int main()
{
    int fd, flag, rd_num = 0;
    struct termios term;
    struct timeval timeout;
    speed_t baud_rate_i, baud_rate_o;
    char recv_buf[100];
    fd = open("/dev/ttyS0", O_RDWR | O_NONBLOCK);
    if (fd == -1)
        printf("can not open the COM1!\n");
    else
        printf("open COM1 ok!\n");

    flag = tcgetattr(fd, &term);
    baud_rate_i = cfgetispeed(&term);
    baud_rate_o = cfgetospeed(&term);
    printf("设置之前的输入波特率是%d，输出波特率是%d\n", baud_rate_i, baud_rate_o);

    set_speed(fd, 115200);

    flag = tcgetattr(fd, &term);
    baud_rate_i = cfgetispeed(&term);
    baud_rate_o = cfgetospeed(&term);
    printf("设置之后的输入波特率是%d，输出波特率是%d\n", baud_rate_i, baud_rate_o);

    if (set_Parity(fd, 8, 1, 'N') == FALSE)
    {
        printf("Set Parity Error\n");
        exit(1);
    }

    int transfer_started = 0;
    int i = 0;
    while (1)
    {

        rd_num = read(fd, recv_buf, sizeof(recv_buf));
        timeout.tv_sec = 0;
        timeout.tv_usec = 200000;
        if (rd_num > 0)
        {
            puts("********************************");
            fflush(stdout);

            // printf("%d(间隔%4.3fs)：we can read \"%s\" from the COM1,total:%d characters.\n", ++i, timeout.tv_sec + timeout.tv_usec * 0.000001, recv_buf, rd_num);
            transfer_started = 1;
            if (!handle(fd, recv_buf, rd_num))
            {
                uart_send(fd, "fail", 4);
            }
        }
        select(0, NULL, NULL, NULL, &timeout); /*精确定时*/
    }
}

int speed_arr[] = {B115200, B38400, B19200, B9600, B4800, B2400, B1200, B300};
int name_arr[] = {115200, 38400, 19200, 9600, 4800, 2400, 1200, 300};
void set_speed(int fd, int speed)
{
    unsigned int i;
    int status;
    struct termios Opt;
    tcgetattr(fd, &Opt);
    for (i = 0; i < sizeof(speed_arr) / sizeof(int); i++)
    {
        if (speed == name_arr[i])
        {
            tcflush(fd, TCIOFLUSH);
            cfsetispeed(&Opt, speed_arr[i]);
            cfsetospeed(&Opt, speed_arr[i]);
            status = tcsetattr(fd, TCSANOW, &Opt);
            if (status != 0)
            {
                perror("tcsetattr fd1");
                return;
            }
            tcflush(fd, TCIOFLUSH);
        }
    }
}

/**
*@brief   设置串口数据位，停止位和效验位
*@param fd     类型 int 打开的串口文件句柄*
*@param databits 类型 int 数据位   取值 为 7 或者8*
*@param stopbits 类型 int 停止位   取值为 1 或者2*
*@param parity 类型 int 效验类型 取值为N,E,O,,S
*/
int set_Parity(int fd, int databits, int stopbits, int parity)
{
    struct termios options;
    if (tcgetattr(fd, &options) != 0)
    {
        perror("SetupSerial 1");
        return (FALSE);
    }
    options.c_cflag &= ~CSIZE;
    switch (databits) /*设置数据位数*/
    {
    case 7:
        options.c_cflag |= CS7;
        break;
    case 8:
        options.c_cflag |= CS8;
        break;
    default:
        fprintf(stderr, "Unsupported data size\n");
        return (FALSE);
    }
    switch (parity)
    {
    case 'n':
    case 'N':
        //        options.c_cflag &= ~PARENB;   /* Clear parity enable */
        //        options.c_iflag &= ~INPCK;     /* Enable parity checking */
        options.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG); /*Input*/
        options.c_oflag &= ~OPOST;                          /*Output*/
        break;
    case 'o':
    case 'O':
        options.c_cflag |= (PARODD | PARENB); /* 设置为奇效验*/
        options.c_iflag |= INPCK;             /* Disnable parity checking */
        break;
    case 'e':
    case 'E':
        options.c_cflag |= PARENB;  /* Enable parity */
        options.c_cflag &= ~PARODD; /* 转换为偶效验*/
        options.c_iflag |= INPCK;   /* Disnable parity checking */
        break;
    case 'S':
    case 's': /*as no parity*/
        options.c_cflag &= ~PARENB;
        options.c_cflag &= ~CSTOPB;
        break;
    default:
        fprintf(stderr, "Unsupported parity\n");
        return (FALSE);
    }
    /* 设置停止位*/
    switch (stopbits)
    {
    case 1:
        options.c_cflag &= ~CSTOPB;
        break;
    case 2:
        options.c_cflag |= CSTOPB;
        break;
    default:
        fprintf(stderr, "Unsupported stop bits\n");
        return (FALSE);
    }
    /* Set input parity option */
    if ((parity != 'n') && (parity != 'N'))
        options.c_iflag |= INPCK;

    options.c_cc[VTIME] = 5; // 0.5 seconds
    options.c_cc[VMIN] = 1;

    options.c_cflag &= ~HUPCL;
    options.c_iflag &= ~INPCK;
    options.c_iflag |= IGNBRK;
    options.c_iflag &= ~ICRNL;
    options.c_iflag &= ~IXON;
    options.c_lflag &= ~IEXTEN;
    options.c_lflag &= ~ECHOK;
    options.c_lflag &= ~ECHOCTL;
    options.c_lflag &= ~ECHOKE;
    options.c_oflag &= ~ONLCR;

    tcflush(fd, TCIFLUSH); /* Update the options and do it NOW */
    if (tcsetattr(fd, TCSANOW, &options) != 0)
    {
        perror("SetupSerial 3");
        return (FALSE);
    }

    return (TRUE);
}