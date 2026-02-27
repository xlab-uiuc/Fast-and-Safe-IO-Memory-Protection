#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "deps/hiredis/hiredis.h"
#include <vector>
#include <algorithm>
#include <chrono>
#include <iostream>
#include <string>
#include <assert.h>
#include <thread>
#include <map>

using namespace std::chrono;

#define MEMORY_USAGE 1
#define VALUE_SIZE_KB 256 
#define ITER_COUNT 3

using namespace std;

unsigned long current_time_ms()
{
    milliseconds ms = duration_cast< milliseconds >(system_clock::now().time_since_epoch());
    return ms.count();
}

unsigned long current_time_micros()
{
    microseconds ms = duration_cast<microseconds>(system_clock::now().time_since_epoch());
    return ms.count();
}

void populate(int start, int size, size_t value_size_in_bytes, const char* hostname, int start_port, int num_shards)
{
    redisReply* reply;
    int idx;
    int response = 1;
    int ground_truth = 2;
    redisContext* shards[num_shards];
    struct timeval timeout = { 1, 500000 };

    for(idx = 0; idx < num_shards; ++idx)
    {
        shards[idx] = redisConnectWithTimeout(hostname, start_port + idx, timeout);
    }

    char* value = (char*) malloc(value_size_in_bytes);

    for(idx = 0; idx < value_size_in_bytes; ++idx)
    {
        value[idx] = 'a';
    }

    cout << "Value size is: " << std::to_string(strlen(value)) << endl;
    cout << "thread " << std::to_string(start) << " starting to populate " << size << endl;
    int key_len = sizeof(int);
    char cstr[key_len];

    for(idx = start; idx < start + size; ++idx)
    {
        redisContext* c = shards[idx % num_shards];
        memcpy(cstr, &idx, key_len);
        memcpy(value, &idx, sizeof(int));
        reply = (redisReply*) redisCommand(c,"SET %b %b", cstr, key_len, value, value_size_in_bytes);
        if(reply == NULL)
        {
            printf("Error while setting %s", cstr);
        }
        freeReplyObject(reply);
        reply = (redisReply*) redisCommand(c, "GET %b", cstr, sizeof(int));
        assert(reply->len==value_size_in_bytes);
        memcpy(&response, reply->str, sizeof(int));
        memcpy(&ground_truth, cstr, sizeof(int));
        assert(response==ground_truth);
        freeReplyObject(reply);

        if(idx % 100000 == 0)
        {
            printf("Done populating %d in thread %d\n", idx, start);
        }
    }
    free(value);
    for(idx = 0; idx < num_shards; ++idx)
    {
        redisFree(shards[idx]);
    }
    cout << "thread " << std::to_string(start) << " done populating " << size << endl;
}

int main(int argc, char **argv) {

    unsigned int j, isunix = 0;
    redisContext *c;
    redisReply *reply;
    const char *hostname = (argc > 1) ? argv[1] : "192.168.10.117";
    int port = (argc > 2) ? atoi(argv[2]) : 6379;
    int thread_count = (argc > 3) ? atoi(argv[3]) : 1;
    double memory_usage = (argc > 4) ? atof(argv[4]) : MEMORY_USAGE;
    int num_shards = (argc > 5) ? atoi(argv[5]) : 1;

    struct timeval timeout = { 1, 500000 }; // 1.5 seconds
    int idx;
    vector<char*> keys;
    vector<int> key_sizes;

    int loop_counter = 0;
    thread work_threads[thread_count + 1]; // extra thread to accommodate spill over thread

    int number_of_key_vals = memory_usage * 1024 * 1024 / VALUE_SIZE_KB;
    printf("Going to populate %d key value pairs\n", number_of_key_vals);
    size_t value_size_in_bytes = VALUE_SIZE_KB * 1024;

    int key_vals_in_one_thread = number_of_key_vals / thread_count;
    int thread_idx = 0;
    idx = 0;

    while(idx < number_of_key_vals)
    {
        int size = idx + key_vals_in_one_thread < number_of_key_vals ? key_vals_in_one_thread : number_of_key_vals - idx;
        work_threads[thread_idx] = thread(populate, idx, size, value_size_in_bytes, hostname, port, num_shards);
        ++thread_idx;
        idx += size;
    }

    cout << "waiting for threads to join" << endl;
    for(idx = 0; idx < thread_idx; ++idx)
    {
        work_threads[idx].join();
    }
    /* Disconnects and frees the context */
    cout << "Number of key vals in one thread: " << std::to_string(number_of_key_vals / thread_count) << endl;
    return 0;
}
