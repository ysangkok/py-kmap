#!/bin/sh
curl --data-binary "names=a%2Cb%2Cc%2Cd%2Ce%2Cf%2Cg%2Ch%2Ci%2Cj&funstr=a+and+%28not+b+and+not+d+or+b+and+c+and+not+d%29&type=big&userdata=1011011111%0D%0A1111100111%0D%0A1101111111%0D%0A1011011011%0D%0A1010001010%0D%0A1000111011%0D%0A0011111011" http://localhost:8080/
