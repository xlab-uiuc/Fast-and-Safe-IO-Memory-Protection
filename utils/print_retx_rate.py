import sys
INPUT_FILE = sys.argv[1]
TIME_INT = int(sys.argv[2])

retx_pre = -1
retx_post = -1
sent_pre = -1
sent_post = -1
recv_pre = -1
recv_post = -1
loss_retx_pre = -1
loss_retx_post = -1

# IP-level stats from netstat -s (Ip: and IpExt: sections)
ip_rx_pkts_pre  = -1   # "total packets received"
ip_rx_pkts_post = -1
ip_tx_pkts_pre  = -1   # "requests sent out"
ip_tx_pkts_post = -1
ip_rx_bytes_pre  = -1  # IpExt InOctets
ip_rx_bytes_post = -1
ip_tx_bytes_pre  = -1  # IpExt OutOctets
ip_tx_bytes_post = -1

# Link-level stats from `ip -s link show dev <intf>`
# Header line: "RX: bytes  packets  errors  dropped overrun mcast"
# Data line:   "<bytes>  <packets>  <errors>  <dropped>  <overrun>  <mcast>"
rx_bytes_pre  = -1
rx_pkts_pre   = -1
tx_bytes_pre  = -1
tx_pkts_pre   = -1
rx_bytes_post = -1
rx_pkts_post  = -1
tx_bytes_post = -1
tx_pkts_post  = -1

next_is_rx = False
next_is_tx = False

with open(INPUT_FILE) as f1:
    for line in f1:
        line_str = line.split()
        if not line_str:
            next_is_rx = False
            next_is_tx = False
            continue

        # Link-level RX data line (immediately follows "RX:" header)
        if next_is_rx:
            next_is_rx = False
            b, p = int(line_str[0]), int(line_str[1])
            if rx_bytes_pre == -1:
                rx_bytes_pre, rx_pkts_pre = b, p
            else:
                rx_bytes_post, rx_pkts_post = b, p
            continue

        # Link-level TX data line (immediately follows "TX:" header)
        if next_is_tx:
            next_is_tx = False
            b, p = int(line_str[0]), int(line_str[1])
            if tx_bytes_pre == -1:
                tx_bytes_pre, tx_pkts_pre = b, p
            else:
                tx_bytes_post, tx_pkts_post = b, p
            continue

        # Detect link-level header lines
        if line_str[0] == "RX:":
            next_is_rx = True
            continue
        if line_str[0] == "TX:":
            next_is_tx = True
            continue

        # TCP stats
        if len(line_str) >= 3:
            if line_str[1] == "segments" and line_str[2] == "retransmitted":
                if retx_pre == -1:
                    retx_pre = int(line_str[0])
                else:
                    retx_post = int(line_str[0])
            if line_str[1] == "segments" and line_str[2] == "sent":
                if sent_pre == -1:
                    sent_pre = int(line_str[0])
                else:
                    sent_post = int(line_str[0])
            if line_str[1] == "segments" and line_str[2] == "received":
                if recv_pre == -1:
                    recv_pre = int(line_str[0])
                else:
                    recv_post = int(line_str[0])

        if line_str[0] == "TCPLostRetransmit:":
            if loss_retx_pre == -1:
                loss_retx_pre = int(line_str[1])
            else:
                loss_retx_post = int(line_str[1])

        # IP-level packet counts (Ip: section)
        # "  4855303788 total packets received"
        if len(line_str) >= 4 and line_str[1] == "total" and line_str[2] == "packets" and line_str[3] == "received":
            if ip_rx_pkts_pre == -1:
                ip_rx_pkts_pre = int(line_str[0])
            else:
                ip_rx_pkts_post = int(line_str[0])
        # "  1387424261 requests sent out"
        if len(line_str) >= 4 and line_str[1] == "requests" and line_str[2] == "sent" and line_str[3] == "out":
            if ip_tx_pkts_pre == -1:
                ip_tx_pkts_pre = int(line_str[0])
            else:
                ip_tx_pkts_post = int(line_str[0])

        # IP-level byte counts (IpExt: section)
        # "    InOctets: 199238655506341"
        if line_str[0] == "InOctets:":
            if ip_rx_bytes_pre == -1:
                ip_rx_bytes_pre = int(line_str[1])
            else:
                ip_rx_bytes_post = int(line_str[1])
        # "    OutOctets: 72201769132"
        if line_str[0] == "OutOctets:":
            if ip_tx_bytes_pre == -1:
                ip_tx_bytes_pre = int(line_str[1])
            else:
                ip_tx_bytes_post = int(line_str[1])

assert retx_pre != -1
assert retx_post != -1
assert sent_pre != -1
assert sent_post != -1
assert recv_pre != -1
assert recv_post != -1
# assert(loss_retx_pre != -1)
# assert(loss_retx_post != -1)

retx     = float(retx_post - retx_pre)
loss_retx = float(loss_retx_post - loss_retx_pre)
sent     = float(sent_post - sent_pre)
recv     = float(recv_post - recv_pre)

if sent > 0:
    retx_rate      = retx / sent * 100.0
    loss_retx_rate = loss_retx / sent * 100.0
else:
    retx_rate      = 0
    loss_retx_rate = 0

print("Retx: ",            retx)
print("Loss_retx: ",       loss_retx)
print("Sent: ",            sent)
print("Recv: ",            recv)
print("Time: ",            TIME_INT)
print("Retx_percent: ",    retx_rate)
print("Loss_retx_percent:", loss_retx_rate)
print("Send_rate: ",       float(sent) / TIME_INT)
print("Recv_rate: ",       float(recv) / TIME_INT)

# IP-level stats (only printed if both snapshots were found)
if ip_rx_pkts_pre != -1 and ip_rx_pkts_post != -1:
    ip_rx_pkts = ip_rx_pkts_post - ip_rx_pkts_pre
    print("IP_RX_packets: ",      ip_rx_pkts)
    print("IP_RX_packet_rate: ",  float(ip_rx_pkts) / TIME_INT)

if ip_tx_pkts_pre != -1 and ip_tx_pkts_post != -1:
    ip_tx_pkts = ip_tx_pkts_post - ip_tx_pkts_pre
    print("IP_TX_packets: ",      ip_tx_pkts)
    print("IP_TX_packet_rate: ",  float(ip_tx_pkts) / TIME_INT)

if ip_rx_bytes_pre != -1 and ip_rx_bytes_post != -1:
    ip_rx_bytes = ip_rx_bytes_post - ip_rx_bytes_pre
    print("IP_RX_bytes: ",        ip_rx_bytes)
    print("IP_RX_byte_rate: ",    float(ip_rx_bytes) / TIME_INT)

if ip_tx_bytes_pre != -1 and ip_tx_bytes_post != -1:
    ip_tx_bytes = ip_tx_bytes_post - ip_tx_bytes_pre
    print("IP_TX_bytes: ",        ip_tx_bytes)
    print("IP_TX_byte_rate: ",    float(ip_tx_bytes) / TIME_INT)

# Link-level stats (only printed if both snapshots were found)
if rx_bytes_pre != -1 and rx_bytes_post != -1:
    rx_bytes = rx_bytes_post - rx_bytes_pre
    rx_pkts  = rx_pkts_post  - rx_pkts_pre
    print("Link_RX_bytes: ",   rx_bytes)
    print("Link_RX_packets: ", rx_pkts)
    print("Link_RX_byte_rate: ",   float(rx_bytes) / TIME_INT)
    print("Link_RX_packet_rate: ", float(rx_pkts)  / TIME_INT)

if tx_bytes_pre != -1 and tx_bytes_post != -1:
    tx_bytes = tx_bytes_post - tx_bytes_pre
    tx_pkts  = tx_pkts_post  - tx_pkts_pre
    print("Link_TX_bytes: ",   tx_bytes)
    print("Link_TX_packets: ", tx_pkts)
    print("Link_TX_byte_rate: ",   float(tx_bytes) / TIME_INT)
    print("Link_TX_packet_rate: ", float(tx_pkts)  / TIME_INT)
