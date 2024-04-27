def do_connect():
    import network
    import time
    ssid ="F"
    pwd = "n"

    wifi = network.WLAN(network.STA_IF)

    wifi.active(True)
    wifi.scan()
    wifi.connect(ssid, pwd)
    while not wifi.isconnected():
        print("baglanılıyor")
        print("\n")
        time.sleep(1)
    print(wifi.ifconfig())
    print("\n")
    print("baglandı")
