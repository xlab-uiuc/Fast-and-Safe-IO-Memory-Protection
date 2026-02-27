#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "deps/hiredis/hiredis.h"
#include <vector>
#include <algorithm>
#include <numeric>
#include <chrono>
#include <iostream>
#include <string>
#include <assert.h>
#include <mutex>
#include <thread>
#include <random>
#include <map>
#include "deps/hiredis/async.h"
#include "deps/hiredis/adapters/libevent.h"

using namespace std::chrono;

#define MEMORY_USAGE 0.75
#define VALUE_SIZE_KB 256 
#define ITER_COUNT 1
#define LOG_INTERVAL 1
#define READ_PERCENTAGE 0 

using namespace std;

mutex mtx;
vector<int> read_keys;
vector<unsigned long> average_latencies;
vector<unsigned long> tail_latencies;
vector<unsigned long> all_latencies;
vector<unsigned long*> moving_tpt_idxs;
vector<unsigned long> prev_moving_tpt_idxs;
map<int, vector<unsigned long>*> moving_throughputs;

unsigned long gstart = -1;
unsigned long gend = -1;
int EXP_LENGTH_S = 60;

unsigned long moving_throughput = 0;
int num_threads_added = 0;
int num_threads = 0;
int log_interval_ms = 1000;
int global_read = 0;
int global_set = 0;
int max_moving_recorded = 0;

struct loop_context {
    redisAsyncContext** shards;
    int num_shards;
    int start_port;
    vector<char*>* key_params;
    int ground_truth;
    unsigned long req_start_time;
    unsigned long request_idx;
    vector<int>* latencies;
    default_random_engine* generator;
    uniform_int_distribution<int>* distribution;
    int total_get;
    int total_set;
    int id;
    char* set_value;
};

void get_callback(redisAsyncContext *c, void *r, void *priv_data);
void set_callback(redisAsyncContext *c, void *r, void *priv_data);
void make_request(struct loop_context* loop_ctx);
void disconnect_callback(const redisAsyncContext *c, int status);
void connect_callback(const redisAsyncContext *c, int status);
void moving_tpt_logger();

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

void make_request(struct loop_context* loop_ctx)
{
    redisAsyncContext* c;
    int key_idx = (*(loop_ctx->distribution))(*(loop_ctx->generator));
    int key_val = *((int *)(*loop_ctx->key_params)[key_idx]);
    c = loop_ctx->shards[key_val % loop_ctx->num_shards];
    memcpy(&loop_ctx->ground_truth, &key_val, sizeof(int));
    loop_ctx->req_start_time = current_time_micros();
    // cout << "Ground truth is: " << std::to_string(loop_ctx->ground_truth) << " key val is " << std::to_string(key_val) << " id: " << std::to_string(loop_ctx->id) << " key idx is " << std::to_string(key_idx)  << " key params size: " << std::to_string(loop_ctx->key_params->size()) << endl;

    if(loop_ctx->request_idx % 100 < READ_PERCENTAGE)
    {
        redisAsyncCommand(c, get_callback, loop_ctx, "GET %b", (*loop_ctx->key_params)[key_idx], sizeof(int));
        ++loop_ctx->total_get;
    }
    else
    {
        size_t value_size_in_bytes = VALUE_SIZE_KB * 1024;
        char* value = (char*) malloc(value_size_in_bytes);
        int idx;

        for(idx = 0; idx < value_size_in_bytes; ++idx)
        {
            value[idx] = 'a';
        }
        memcpy(value, (*loop_ctx->key_params)[key_idx], sizeof(int));

        loop_ctx->set_value = value;
        redisAsyncCommand(c, set_callback, loop_ctx, "SET %b %b", (*loop_ctx->key_params)[key_idx], sizeof(int), value, value_size_in_bytes);
        ++loop_ctx->total_set;
    }
}

void connect_callback(const redisAsyncContext *c, int status) {
    if (status != REDIS_OK) {
        printf("connect fail\n");
	printf("Error: %s\n", c->errstr);
        return;
    }
    //printf("Connected...\n");
}

void disconnect_callback(const redisAsyncContext *c, int status) {
    if (status != REDIS_OK) {
        printf("Error: %s\n", c->errstr);
        return;
    }
    //printf("Disconnected...\n");
}

void set_callback(redisAsyncContext *c, void *r, void *priv_data) {
    redisReply *reply = (redisReply*) r;
    struct loop_context* loop_ctx;
    unsigned long req_end_time = current_time_micros();
    unsigned long time_taken;
    int response;
    size_t value_size_in_bytes = VALUE_SIZE_KB * 1024;
    
    if (reply == NULL) {
        if (c->errstr) {
            printf("errstr: %s\n", c->errstr);
        }
    }
    loop_ctx = (struct loop_context*) priv_data;
    time_taken = req_end_time - loop_ctx->req_start_time;
    loop_ctx->latencies->push_back(time_taken);
    ++loop_ctx->request_idx;
    free(loop_ctx->set_value);

    make_request(loop_ctx);
}

void get_callback(redisAsyncContext *c, void *r, void *priv_data) {
    redisReply *reply = (redisReply*) r;
    struct loop_context* loop_ctx;
    unsigned long req_end_time = current_time_micros();
    unsigned long time_taken;
    int response;
    size_t value_size_in_bytes = VALUE_SIZE_KB * 1024;
    
    if (reply == NULL) {
        if (c->errstr) {
            printf("errstr: %s\n", c->errstr);
        }
    }
    loop_ctx = (struct loop_context*) priv_data;

    memcpy(&response, reply->str, sizeof(int));
    // assert(reply->len==value_size_in_bytes);
    // if(loop_ctx->request_idx % 100 == 0)
    // {
    //     cout << "Response is : " << std::to_string(response) << " ground is: " << std::to_string(loop_ctx->ground_truth) << "Loop ID: " << std::to_string(loop_ctx->id) << endl;
    // }
    // assert(response==loop_ctx->ground_truth);

    time_taken = req_end_time - loop_ctx->req_start_time;
    loop_ctx->latencies->push_back(time_taken);
    ++loop_ctx->request_idx;

    make_request(loop_ctx);
}

void read_all(int thread_id, vector<char*>* keys_param, const char* hostname, int start_port, int num_shards, int q_depth)
{
    struct event_base* base = event_base_new();
    redisAsyncContext** shards = new redisAsyncContext*[num_shards];
    vector<struct loop_context*> loop_ctxs;
    struct timeval wait_interval;
    //printf("read all \n");
    for(int idx = 0; idx < num_shards; ++idx)
    {
	//printf("start port:%d\n", start_port);
        redisOptions options = {0};
        REDIS_OPTIONS_SET_TCP(&options, hostname, start_port);
        struct timeval tv = {0};
        tv.tv_sec = 100;
        options.connect_timeout = &tv;
        shards[idx] = redisAsyncConnectWithOptions(&options);
        if (shards[idx]->err) {
            /* Let *c leak for now... */
            //printf("reach here\n");
	    //printf("Error: %s\n", shards[idx]->errstr);
            return;
        }
        // cout << "Created async context for: " << std::to_string(start_port) << endl;
        redisLibeventAttach(shards[idx], base);
        redisAsyncSetConnectCallback(shards[idx], connect_callback);
        redisAsyncSetDisconnectCallback(shards[idx], disconnect_callback);
        ++start_port;
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(10));

    for(int idx = 0; idx < q_depth; ++idx)
    {
        // create loop contexts and make requests
        struct loop_context* loop_ctx = (struct loop_context*) malloc(sizeof(loop_context));
        loop_ctx->distribution = new uniform_int_distribution<int>(0, keys_param->size() - 1);
        loop_ctx->generator = new default_random_engine(idx + 1);

        int test = (*loop_ctx->distribution)(*loop_ctx->generator);
        // cout << "Test initial value for idx: " << std::to_string(idx) << " is " << std::to_string(test) << endl;
        loop_ctx->latencies = new vector<int>();
        loop_ctx->num_shards = num_shards;
        loop_ctx->shards = shards;
        loop_ctx->start_port = start_port;
        loop_ctx->request_idx = 0;
        loop_ctx->total_get = 0;
        loop_ctx->total_set = 0;
        loop_ctx->key_params = keys_param;
        loop_ctx->id = idx;

        make_request(loop_ctx);

        loop_ctxs.push_back(loop_ctx);
        mtx.lock();
        moving_tpt_idxs.push_back(&(loop_ctx->request_idx));
        prev_moving_tpt_idxs.push_back(0);
        mtx.unlock();
    }


    wait_interval.tv_sec = EXP_LENGTH_S;
    wait_interval.tv_usec = 0;
    event_base_loopexit(base, &wait_interval);
    event_base_dispatch(base);

    mtx.lock();
    
    for(int idx = 0; idx < q_depth; ++idx)
    {
        struct loop_context* loop_ctx = loop_ctxs[idx];
        vector<int> latencies = *(loop_ctx->latencies);
        read_keys.push_back(loop_ctx->request_idx);
        // cout << "Total count:[" << std::to_string(thread_id) << "] " << std::to_string(read_keys_size) << endl; 

        unsigned long average_latency = accumulate(latencies.begin(), latencies.end(), 0.0) / latencies.size();
        // cout << "Average latency:[" << std::to_string(thread_id) << "] " << std::to_string(average_latency) << endl;
        average_latencies.push_back(average_latency);

        all_latencies.insert(all_latencies.end(), latencies.begin(), latencies.end());

        sort(latencies.begin(), latencies.end());
        int tail_idx = latencies.size() * 0.95;
        // cout << "95th latency:[" << std::to_string(thread_id) << "] " << std::to_string(latencies[tail_idx]) << endl;
        tail_latencies.push_back(latencies[tail_idx]);

        global_read += loop_ctx->total_get;
        global_set += loop_ctx->total_set;
    }

    mtx.unlock();

    // consolidate throughputs and latencies
    delete[] shards;
}

void moving_tpt_logger()
{
    // vector<unsigned long> prev_moving_tpt_idxs;
    // vector<unsigned long*> moving_tpt_idxs;

    long start_time = current_time_ms();
    int idx;
    while(current_time_ms() - start_time < EXP_LENGTH_S * 1000)
    {
        double total_idxs = 0;
        double throughput = 0;
        this_thread::sleep_for(std::chrono::seconds(LOG_INTERVAL));
        for(idx = 0; idx < moving_tpt_idxs.size(); ++idx)
        {
            unsigned long curr_idxs = *(moving_tpt_idxs[idx]);
            unsigned long prev_idxs = prev_moving_tpt_idxs[idx];

            total_idxs += curr_idxs - prev_idxs;
            prev_moving_tpt_idxs[idx] = curr_idxs;
        }
        throughput = ((total_idxs) * 1.0) / LOG_INTERVAL; 
        //cout << "Moving throughput " << std::to_string(throughput) << " " << std::to_string(current_time_ms()) << endl;
    }
}

int main(int argc, char **argv) {

    unsigned int j, isunix = 0;
    redisContext *c;
    redisReply *reply;
    const char *hostname = (argc > 1) ? argv[1] : "192.168.10.117";
    int port = (argc > 2) ? atoi(argv[2]) : 6379;
    int thread_count = (argc > 3) ? atoi(argv[3]) : 8;
    double memory_usage = (argc > 4) ? atof(argv[4]) : MEMORY_USAGE;
    int num_shards = (argc > 5) ? atoi(argv[5]) : 1;
    int q_depth = (argc > 6) ? atoi(argv[6]) : 1;
    EXP_LENGTH_S = (argc > 7) ? atoi(argv[7]) : 30;
    //cout << "EXP length: " << std::to_string(EXP_LENGTH_S) << endl;

    struct timeval timeout = { 1, 500000 }; // 1.5 seconds
    int idx;
    vector<char*> keys;
    vector<int> key_sizes;
    int loop_counter = 0;
    thread work_threads[thread_count + 1]; // extra thread for spillover
    thread logger_thread;
    int thread_idx = 0;

    int number_of_key_vals = memory_usage * 1024 * 1024 / VALUE_SIZE_KB;
    //printf("Going to access %d key value pairs\n", number_of_key_vals);
    size_t value_size_in_bytes = VALUE_SIZE_KB * 1024;
    char* value = (char*) malloc(value_size_in_bytes);

    for(idx = 0; idx < value_size_in_bytes; ++idx)
    {
        value[idx] = 'a';
    }
    //printf("Done generating the value to be used\n");
    //cout << "Value size is: " << std::to_string(strlen(value)) << endl;
    for(idx = 0; idx < number_of_key_vals; ++idx)
    {
        int key_len = sizeof(int);
        char* cstr = new char[key_len];
        memcpy(cstr, &idx, key_len);
        keys.push_back(cstr);
    }
    unsigned long start = current_time_ms();

    int num_keys_per_thread = number_of_key_vals / thread_count;
    //cout << "Number of keys per thread: " << std::to_string(num_keys_per_thread) << endl;
    idx = 0;

    
    for(idx = 0; idx < thread_count; ++idx)
    {
        // increment port here and round robin
        work_threads[idx] = thread(read_all, idx, &keys, hostname, port, num_shards, q_depth);
    }

    logger_thread = thread(moving_tpt_logger);
    //cout << "Start time: " << std::to_string(current_time_ms()) << endl;
    for(idx = 0; idx < thread_count; ++idx)
    {
        work_threads[idx].join();
    }
    unsigned long end = current_time_ms();
    //cout << "End time: " << std::to_string(current_time_ms()) << endl;
    logger_thread.join();
    //cout << "Done waiting for logger thread" << endl;

    int time_taken = (end - start) / 1000;
    int throughput = (accumulate(read_keys.begin(), read_keys.end(), 0.0) / time_taken) / 1000;
    long average_latency = (accumulate(average_latencies.begin(), average_latencies.end(), 0.0) / average_latencies.size());
    long average_tail_latency = (accumulate(tail_latencies.begin(), tail_latencies.end(), 0.0) / tail_latencies.size());

    //cout << "Time taken: " << std::to_string(time_taken) << endl;
    cout << "Throughput: " << std::to_string(throughput) << "(kiops)" << endl;
    //cout << "Average latency: " << std::to_string(average_latency) << endl;
    cout << "Tail latency: " << std::to_string(average_tail_latency) << "(us)" << endl;
    //cout << "Total read: " << std::to_string(global_read) << endl;
    //cout << "Total set: " << std::to_string(global_set) << endl;
    //cout << "Percentage read: " << std::to_string(global_read * 1.0 / (global_read + global_set) * 100) << endl; 
    //cout << "All latencies size: " << std::to_string(all_latencies.size()) << endl;

    // for(idx = 0; idx < all_latencies.size(); ++idx)
    // {
    //     if(idx % 100)
    //     {
    //         cout << "Dist_latency: " << std::to_string(all_latencies[idx]) << endl;
    //     }
    // }
    /* Disconnects and frees the context */
    free(value);

    // for(idx = 0; idx < max_moving_recorded; ++idx)
    // {
    //     unsigned long total = 0;
    //     int added = 0;
    //     for(int thread_id = 0; thread_id < thread_count; ++thread_id)
    //     {
    //         vector<unsigned long> moving_totals = *(moving_throughputs[thread_id]);
    //         if(idx < moving_totals.size())
    //         {
    //             total += moving_totals[idx];
    //         }
    //     }
    //     if(added == thread_count)
    //     {
    //         // cout << "Moving throughput: " << (total / log_interval_ms / 1000) << endl;
    //     }
    // }
    return 0;
}

// sudo ./perf stat -e dTLB-loads,dTLB-load-misses,dTLB-stores,dTLB-store-misses -e cpu/event=0x08,umask=0x10,name=dcycles -e cpu/event=0x85,umask=0x10,name=icycles/ -a -I 1000
// sudo ./perf stat -e cpu/event=0x08,umask=0x10,name=dcycles/ -e cpu/event=0x85,umask=0x10,name=icycles/ -e cpu/event=0xbc,umask=0x18,name=dreads -e cpu/event=0xbc,umask=0x28,name=ireads -e dTLB-loads,dTLB-load-misses,dTLB-stores,dTLB-store-misses,iTLB-load,iTLB-load-misses -a -I 1000
// g++ -g async.c -o redis_async -lpthread -lhiredis -levent
// abhishek@genie07:~/vm_stuff/nsdi_eval/redis$ gdb --args ./redis_async hc1 6379 1 4 4 2
