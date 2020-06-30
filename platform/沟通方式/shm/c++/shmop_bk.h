#ifndef SHMOP_H_INCLUDED
#define SHMOP_H_INCLUDED

bool shm_init(int cam_id, int thread_id);
int shm_get_data_size();
int shm_get_data(char* dest);
bool shm_send_data(char* src, int str_len, char* expand);
void shm_stop();

#endif // SHMOP_H_INCLUDED
