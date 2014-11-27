import os
import subprocess

from django.core.context_processors import csrf, request
from django.forms.formsets import BaseFormSet, formset_factory
from django.shortcuts import render, render_to_response

from monitorWebApp.configure_form import configure_form
from webapp.settings import BASE_DIR


# Create your views here.
def main (request):
    request.session["vm_time_counter"] = str(0.0)
    if not request.session["vm_select"]:
        request.session["vm_select"] = "vm1"
    
    
    
    args = {}
    args.update(csrf(request))
    

    if request.session["external_ips"]:
        
        external_ips = request.session["external_ips"]
        print "in main " 
        print external_ips
        num = 0
        vm_tag =[]
        while(num<len(external_ips)):
            vm = "vm"+str(num+1)
            vm_tag.append(vm)
            num +=1
        print vm_tag
        args ['vm_numbers'] = vm_tag
    
    return render_to_response('main.html', args)


#################################################################################
##
##    Function to Configure Virtual Machines
##
#################################################################################

def configure (request):
    
    if not request.session["vm_select"]:
        request.session["vm_select"] = "vm1"
    
    # This class is used to make empty formset forms required
    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False

    configureFormSet = formset_factory(configure_form, formset=RequiredFormSet)
    
    if request.method == 'POST': # If the form has been submitted...
        
        # Create a formset from the submitted data
        configure_formset_raw = configureFormSet(request.POST, request.FILES)
        print "==================================="
        print configure_formset_raw
        
        if configure_formset_raw.is_valid():
            
            external_ips = []
            user_names = []
            
            for form in configure_formset_raw.forms:
                config_form = form.cleaned_data
                external_ip = config_form.get('external_ip')
                user_name = config_form.get('user_name')
                #print "+++++++++++++++++++++++++++++++++++++++"
                #print external_ip
                #print user_name
                external_ips.append(external_ip)
                user_names.append(user_name)
            
            print "000000000000000"
            print external_ips
            print user_names

            request.session["external_ips"] = external_ips
            request.session["user_names"] = user_names
            
            args_done = {}
            args_done.update(csrf(request))
        
            args_done['external_ips'] = external_ips
            args_done['user_names'] = user_names
            
            num = 0
            vm_tag =[]
            while(num<len(external_ips)):
                vm = "vm"+str(num+1)
                vm_tag.append(vm)
                num +=1
            print vm_tag
            args_done ['vm_numbers'] = vm_tag
            
            return render_to_response('configure_done.html', args_done)
    else:
        configure_formset_raw = configureFormSet()
    
    args = {'configure_formset_raw': configure_formset_raw,}
    args.update(csrf(request))
    
    return render_to_response('configure.html', args)


#################################################################################
##
##    Function to handle Network Delay
##
#################################################################################

def delay (request, vm_select="vm1"):
    
    print "+++++++++++++++++++++++++"
    print vm_select
    
    vm_select_old = request.session["vm_select"]
    print "vm select old is " + vm_select_old
    
    request.session["vm_select"] = vm_select
    
    
    #obtain parameters
    external_ips = request.session["external_ips"]
    user_names = request.session["user_names"]
        
    #obtain shell directory path
    local_file_name = os.path.join(BASE_DIR, 'static', 'shell', 'local.sh')
    remote_file_name = os.path.join(BASE_DIR, 'static', 'shell', 'remote_ping.sh')
    remove_file_name = os.path.join(BASE_DIR, 'static', 'shell', 'remove_ping_csv.sh')
    shell_path = os.path.join(BASE_DIR, 'static', 'shell')
    print shell_path
    print remove_file_name
    
    
    #construct ip, user name data set
    vm_set = []
    index = 0
    while index < len(external_ips):
        temp_set = []
        temp_set.append(external_ips[index])
        temp_set.append(user_names[index])
        vm_set.append(temp_set)
        index += 1
    print vm_set
    
    vm_total_num = index
    
    
    
    #################filter out selected VM to view#########################
    
    vm_index = int(vm_select.split("vm")[1]) - 1
    print vm_index
    
    #################filter out old VM######################################
    vm_index_old = int(vm_select_old.split("vm")[1]) -1
    print vm_index_old
    
    
    vm_time_counter = float(request.session["vm_time_counter"])

    #################construct remove_ping_csv.sh shell script##############
    if vm_select != vm_select_old or (vm_select == "vm1" and vm_select_old =="vm1" and vm_time_counter == 0.0):
        request.session["vm_time_counter"] = str(0.0)

        if not os.path.exists(os.path.dirname(remove_file_name)):
            os.makedirs(os.path.dirname(remove_file_name))
        with open(remove_file_name, "wb") as f:
            print "need to construct remove shell script"
            host_vm_old = vm_set[vm_index_old][1]+"@"+vm_set[vm_index_old][0]
            f.write("ssh "+ host_vm_old + " \"rm -rf *.csv\"\n")
        subprocess.check_call(["bash", remove_file_name])

    
    #set global counter
    vm_time_counter = float(request.session["vm_time_counter"])
    vm_time_counter += 1
    request.session["vm_time_counter"] = str(vm_time_counter)
    
        
    #################construct remote_ping.sh shell script########################
    if not os.path.exists(os.path.dirname(remote_file_name)):
        print "remote_ping.sh does not exist"
        os.makedirs(os.path.dirname(remote_file_name))
    with open(remote_file_name, "wb") as f:
        print "rewrite remote_ping.sh==========================="
        f.write("if [ -f ping_output.csv ];\n")
        f.write("then\n")
        f.write("\techo \"File $FILE exists\"\n")
        f.write("else\n")
        f.write("\techo \"File $FILE does not exists\"\n")
        text = "\techo \"Time,"
        #f.write("\techo \"Time,vm2,vm3\" >> ping_output.csv\n")

        i = 0
        while(i < vm_total_num):
            if(i!=vm_index):
                text = text+"vm"+str(i+1)+","
            i += 1
        text = text[:-1]
        text = text + "\" >> ping_output.csv\n"
        f.write(text)
        
        f.write("fi\n")
        f.write("\n")
        ###########need to change to loop structure#########
        i = 0
        ping_list = []
        while(i<vm_total_num):
            if (i!= vm_index):  
                f.write("vm"+str(i+1)+"_ping=$(ping -c 2 " + vm_set[i][0] + "| awk '/rtt/ {print $4}'| awk -F'/' '{print $2}');\n")
                ping_list.append("vm"+str(i+1)+"_ping")
            i += 1   
                
            
        f.write("\n")
        ####################################################
        f.write("comma=\",\"\n")
        #f.write("full=\"$1$comma$first_ping$comma$second_ping\"\n")
        text2 = "full=\"$1$comma"
        for ping in ping_list:
            text2 = text2 + "$"+ping+"$comma"
        text2 = text2[:-6]
        text2 = text2 + "\"\n"
        f.write(text2)
        f.write("echo $full >> ping_output.csv\n")
        
    #################construct local.sh shell script########################
    if not os.path.exists(os.path.dirname(local_file_name)):
        print "local.sh does not exist"
        os.makedirs(os.path.dirname(local_file_name))
    with open(local_file_name, "wb") as f:
        print "rewrite local.sh====================="
        #f.write("ssh-keygen -R " + vm_set[vm_index][0] + "\n")
        #f.write("ssh-keyscan -H " + vm_set[vm_index][0] + " >> ~/.ssh/known_hosts\n")
        f.write("#below is vm host ip address\n")
        host_vm = vm_set[vm_index][1]+"@"+vm_set[vm_index][0]
        f.write("ssh " + host_vm +" 'bash -s' < "+ remote_file_name +" $1\n")
        f.write("\n")
        f.write("#remove local bandwidth log file\n")
        #f.write("rm -f *.csv\n") ################fix me?#####################
        f.write("\n")
        f.write("#copy remote bandwidth output log file to local machine\n")
        f.write("#below is vm host ip address\n")
        delay_data_path = os.path.join(BASE_DIR, 'static', 'data', 'delay')
        f.write("scp " + host_vm + ":~/ping_output.csv " + delay_data_path + "\n")
        
    
    #############run local.sh in server####################
    subprocess.check_call(["bash", local_file_name, str(vm_time_counter/2)])
 
    args = {}
    args.update(csrf(request))
    
    num = 0
    vm_tag =[]
    while(num<len(external_ips)):
        vm = "vm"+str(num+1)
        vm_tag.append(vm)
        num +=1
    print vm_tag
        
    args ['vm_numbers'] = vm_tag
    args ['vm_select'] = vm_select
    return render_to_response('delay.html',args)
    
    
#################################################################################
##
##    Function to handle Network Bandwidth
##
#################################################################################

def bandwidth (request, vm_select="vm1"):
    
    print "+++++++++++++++++++++++++"
    print vm_select
    
    vm_select_old = request.session["vm_select"]
    print "vm select old is " + vm_select_old
    
    request.session["vm_select"] = vm_select
    
    
    #obtain parameters
    external_ips = request.session["external_ips"]
    user_names = request.session["user_names"]
        
    #obtain shell directory path
    local_file_name = os.path.join(BASE_DIR, 'static', 'shell', 'local.sh')
    remote_file_name = os.path.join(BASE_DIR, 'static', 'shell', 'bandwidth_c.sh')
    remove_file_name = os.path.join(BASE_DIR, 'static', 'shell', 'remove_bandwidth_csv.sh')
    shell_path = os.path.join(BASE_DIR, 'static', 'shell')
    print shell_path
    print remove_file_name
    
    
    #construct ip, user name data set
    vm_set = []
    index = 0
    while index < len(external_ips):
        temp_set = []
        temp_set.append(external_ips[index])
        temp_set.append(user_names[index])
        vm_set.append(temp_set)
        index += 1
    print vm_set
    
    vm_total_num = index
    
    
    
    #################filter out selected VM to view#########################
    
    vm_index = int(vm_select.split("vm")[1]) - 1
    print vm_index
    
    #################filter out old VM######################################
    vm_index_old = int(vm_select_old.split("vm")[1]) -1
    print vm_index_old
    
    
    vm_time_counter = float(request.session["vm_time_counter"])

    #################construct remove_bandwidth_csv.sh shell script##############
    if vm_select != vm_select_old or (vm_select == "vm1" and vm_select_old =="vm1" and vm_time_counter == 0.0):
        request.session["vm_time_counter"] = str(0.0)

        if not os.path.exists(os.path.dirname(remove_file_name)):
            os.makedirs(os.path.dirname(remove_file_name))
        with open(remove_file_name, "wb") as f:
            print "need to construct remove shell script"
            host_vm_old = vm_set[vm_index_old][1]+"@"+vm_set[vm_index_old][0]
            f.write("ssh "+ host_vm_old + " \"rm -rf *.csv\"\n")
            
        print remove_file_name
        subprocess.check_call(["bash", remove_file_name])

    
    #set global counter
    vm_time_counter = float(request.session["vm_time_counter"])
    vm_time_counter += 1
    request.session["vm_time_counter"] = str(vm_time_counter)
    
    
    #################construct remote.sh shell script########################
    if not os.path.exists(os.path.dirname(remote_file_name)):
        print "bandwidth_c.sh does not exist"
        os.makedirs(os.path.dirname(remote_file_name))
    with open(remote_file_name, "wb") as f:
        print "rewrite bandwidth_c.sh==========================="
        f.write("if [ -f bandwidth_output.csv ];\n")
        f.write("then\n")
        f.write("\techo \"File $FILE exists\"\n")
        f.write("else\n")
        f.write("\techo \"File $FILE does not exists\"\n")
        text = "\techo \"Time,"
        #f.write("\techo \"Time,vm2,vm3\" >> ping_output.csv\n")

        i = 0
        while(i < vm_total_num):
            if(i!=vm_index):
                text = text+"vm"+str(i+1)+","
            i += 1
        text = text[:-1]
        text = text + "\" >> bandwidth_output.csv\n"
        f.write(text)
        
        f.write("fi\n")
        f.write("\n")
        ###########need to change to loop structure#########
        i = 0
        bandwidth_list = []
        while(i<vm_total_num):
            if (i!= vm_index):  
                f.write("vm"+str(i+1)+"_bw=$(iperf -c " + vm_set[i][0] + " -t 2|awk '/Mbits/ {print $8}')\n")
                bandwidth_list.append("vm"+str(i+1)+"_bw")
            i += 1   
                
            
        f.write("\n")
        ####################################################
        f.write("comma=\",\"\n")
        #f.write("full=\"$1$comma$first_ping$comma$second_ping\"\n")
        text2 = "full=\"$1$comma"
        for bandwidth in bandwidth_list:
            text2 = text2 + "$" + bandwidth + "$comma"
        text2 = text2[:-6]
        text2 = text2 + "\"\n"
        f.write(text2)
        f.write("echo $full >> bandwidth_output.csv\n")
        
    #################construct local.sh shell script########################
    if not os.path.exists(os.path.dirname(local_file_name)):
        print "local.sh does not exist"
        os.makedirs(os.path.dirname(local_file_name))
    with open(local_file_name, "wb") as f:
        print "rewrite local.sh====================="
        #f.write("ssh-keygen -R " + vm_set[vm_index][0] + "\n")
        #f.write("ssh-keyscan -H " + vm_set[vm_index][0] + " >> ~/.ssh/known_hosts\n")
        
        #ssh leipeng@130.211.153.18 "iperf -s > out.log &" 
        #ssh leipeng@130.211.164.2 "iperf -s > out.log &" 
        
        i = 0
        while(i<vm_total_num):
            if (i!= vm_index):
                server_vm = vm_set[i][1]+ "@" +vm_set[i][0]  
                f.write("ssh " + server_vm + " \"iperf -s > out.log &\"\n")
            i += 1   
        
        
        f.write("\n")

        #ssh leipeng@130.211.163.194 'bash -s' < bandwidth_c.sh $1 
        host_vm = vm_set[vm_index][1]+"@"+vm_set[vm_index][0]
        f.write("ssh " + host_vm +" 'bash -s' < "+ remote_file_name +" $1\n")
        f.write("\n")
        
        #scp leipeng@130.211.163.194:~/bandwidth_output.csv ~/monitor/bandwidth/

        bandwidth_data_path = os.path.join(BASE_DIR, 'static', 'data', 'bandwidth')
        f.write("scp " + host_vm + ":~/bandwidth_output.csv " + bandwidth_data_path + "\n")
        f.write("\n")

        #ssh leipeng@130.211.153.18 "ps -ef | grep 'iperf' | awk '{print \$2}' | xargs kill" 
        #ssh leipeng@130.211.164.2 "ps -ef | grep 'iperf' | awk '{print \$2}' | xargs kill" 
        '''
        i = 0
        while(i<vm_total_num):
            if (i!= vm_index):
                server_vm = vm_set[i][1]+ "@" +vm_set[i][0]  
                f.write("ssh " + server_vm + " \"ps -ef | grep 'iperf' | awk '{print \$2}' | xargs kill\"\n")
            i += 1 
        '''
    #############run local.sh in server####################
    subprocess.check_call(["bash", local_file_name, str(vm_time_counter/2)])
 
    args = {}
    args.update(csrf(request))
    
    num = 0
    vm_tag =[]
    while(num<len(external_ips)):
        vm = "vm"+str(num+1)
        vm_tag.append(vm)
        num +=1
    print vm_tag
        
    args ['vm_numbers'] = vm_tag
    args ['vm_select'] = vm_select
    return render_to_response('bandwidth.html',args)

#################################################################################
##
##    Function to handle Packet Loss
##
#################################################################################

def packet_loss (request, vm_select="vm1"):
    
    print "+++++++++++++++++++++++++"
    print vm_select
    
    vm_select_old = request.session["vm_select"]
    print "vm select old is " + vm_select_old
    
    request.session["vm_select"] = vm_select
    
    
    #obtain parameters
    external_ips = request.session["external_ips"]
    user_names = request.session["user_names"]
        
    #obtain shell directory path
    local_file_name = os.path.join(BASE_DIR, 'static', 'shell', 'local.sh')
    remote_file_name = os.path.join(BASE_DIR, 'static', 'shell', 'lost_c.sh')
    #terminate_file_name = os.path.join(BASE_DIR, 'static', 'shell', 'terminate_lost.sh')
    remove_file_name = os.path.join(BASE_DIR, 'static', 'shell', 'remove_lost_csv.sh')
    shell_path = os.path.join(BASE_DIR, 'static', 'shell')
    print shell_path
    print remove_file_name
    
    
    #construct ip, user name data set
    vm_set = []
    index = 0
    while index < len(external_ips):
        temp_set = []
        temp_set.append(external_ips[index])
        temp_set.append(user_names[index])
        vm_set.append(temp_set)
        index += 1
    print vm_set
    
    vm_total_num = index
    
    
    
    #################filter out selected VM to view#########################
    
    vm_index = int(vm_select.split("vm")[1]) - 1
    print vm_index
    
    #################filter out old VM######################################
    vm_index_old = int(vm_select_old.split("vm")[1]) -1
    print vm_index_old
    
    
    vm_time_counter = float(request.session["vm_time_counter"])

    #################construct remove_lost_csv.sh shell script##############
    if vm_select != vm_select_old or (vm_select == "vm1" and vm_select_old =="vm1" and vm_time_counter == 0.0):
        request.session["vm_time_counter"] = str(0.0)

        if not os.path.exists(os.path.dirname(remove_file_name)):
            os.makedirs(os.path.dirname(remove_file_name))
        with open(remove_file_name, "wb") as f:
            print "need to construct remove shell script"
            host_vm_old = vm_set[vm_index_old][1]+"@"+vm_set[vm_index_old][0]
            f.write("ssh "+ host_vm_old + " \"rm -rf *.csv\"\n")
            
        print remove_file_name
        subprocess.check_call(["bash", remove_file_name])

    
    #set global counter
    vm_time_counter = float(request.session["vm_time_counter"])
    vm_time_counter += 1
    request.session["vm_time_counter"] = str(vm_time_counter)
    
    
    #################construct remote.sh shell script########################
    if not os.path.exists(os.path.dirname(remote_file_name)):
        print "lost_c.sh does not exist"
        os.makedirs(os.path.dirname(remote_file_name))
    with open(remote_file_name, "wb") as f:
        print "rewrite lost_c.sh==========================="
        f.write("if [ -f lost_output.csv ];\n")
        f.write("then\n")
        f.write("\techo \"File $FILE exists\"\n")
        f.write("else\n")
        f.write("\techo \"File $FILE does not exists\"\n")
        text = "\techo \"Time,"
        #f.write("\techo \"Time,vm2,vm3\" >> ping_output.csv\n")

        i = 0
        while(i < vm_total_num):
            if(i!=vm_index):
                text = text+"vm"+str(i+1)+","
            i += 1
        text = text[:-1]
        text = text + "\" >> lost_output.csv\n"
        f.write(text)
        
        f.write("fi\n")
        f.write("\n")
        ###########need to change to loop structure#########
        #first_lost=$(iperf -c 130.211.153.18 -u -b 10m -l 60 -t 1 -r |awk '/%/ {print $0}'|head -1|cut -d "(" -f2 | cut -d ")" -f1 |sed 's/\%//g')
        #second_lost=$(iperf -c 130.211.164.2 -u -b 10m -l 60 -t 1 -r |awk '/%/ {print $0}'|head -1|cut -d "(" -f2 | cut -d ")" -f1 |sed 's/\%//g')
        
        i = 0
        lost_list = []
        while(i<vm_total_num):
            if (i!= vm_index):  
                f.write("vm"+str(i+1)+"_lost=$(iperf -c " + vm_set[i][0] + " -u -b 10m -l 1000 -t 1 -r |awk '/%/ {print $0}'|head -1|cut -d \"(\" -f2 | cut -d \")\" -f1 |sed 's/\%//g')\n")
                lost_list.append("vm"+str(i+1)+"_lost")
            i += 1   
                
            
        f.write("\n")
        ####################################################
        f.write("comma=\",\"\n")
        #f.write("full=\"$1$comma$first_ping$comma$second_ping\"\n")
        text2 = "full=\"$1$comma"
        for lost in lost_list:
            text2 = text2 + "$" + lost + "$comma"
        text2 = text2[:-6]
        text2 = text2 + "\"\n"
        f.write(text2)
        f.write("echo $full >> lost_output.csv\n")
        
    #################construct local.sh shell script########################
    if not os.path.exists(os.path.dirname(local_file_name)):
        print "local.sh does not exist"
        os.makedirs(os.path.dirname(local_file_name))
    with open(local_file_name, "wb") as f:
        print "rewrite local.sh====================="
        #f.write("ssh-keygen -R " + vm_set[vm_index][0] + "\n")
        #f.write("ssh-keyscan -H " + vm_set[vm_index][0] + " >> ~/.ssh/known_hosts\n")
        
        #ssh leipeng@130.211.153.18 "iperf -s > out.log &" 
        #ssh leipeng@130.211.164.2 "iperf -s > out.log &" 
        
        i = 0
        while(i<vm_total_num):
            if (i!= vm_index):
                server_vm = vm_set[i][1]+ "@" +vm_set[i][0]  
                f.write("ssh " + server_vm + " \"iperf -s -u > out.log &\"\n")
            i += 1   
        
        
        f.write("\n")

        #ssh leipeng@130.211.163.194 'bash -s' < bandwidth_c.sh $1 
        host_vm = vm_set[vm_index][1]+"@"+vm_set[vm_index][0]
        f.write("ssh " + host_vm +" 'bash -s' < "+ remote_file_name +" $1\n")
        f.write("\n")
        
        #scp leipeng@130.211.163.194:~/bandwidth_output.csv ~/monitor/bandwidth/

        lost_data_path = os.path.join(BASE_DIR, 'static', 'data', 'packetLoss')
        f.write("scp " + host_vm + ":~/lost_output.csv " + lost_data_path + "\n")
        f.write("\n")

        
    #############run local.sh in server####################
    subprocess.check_call(["bash", local_file_name, str(vm_time_counter/2)])
 
    args = {}
    args.update(csrf(request))
    
    num = 0
    vm_tag =[]
    while(num<len(external_ips)):
        vm = "vm"+str(num+1)
        vm_tag.append(vm)
        num +=1
    print vm_tag
        
    args ['vm_numbers'] = vm_tag
    args ['vm_select'] = vm_select
    return render_to_response('packet_loss.html',args)

