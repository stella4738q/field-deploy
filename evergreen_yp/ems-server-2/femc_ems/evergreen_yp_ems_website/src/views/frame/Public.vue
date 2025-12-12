<template> 
    <router-view   ></router-view>
</template>

<script>
import newwebsocket from '@/lib/NewWebSocket.js';
import { mapState } from "vuex";

export default {
    components: {
    },
    data() {
        return {
            SocketDataALL: null,
            webSocket: null,
        };
    },
    computed: {
    },
    mounted() {
    },
    beforeUnmount() {
        try {
            this.webSocket.close();
        } catch (e) {

        }
    },
    created() {
        this.CreateSocket();
    },
    watch: {
    },
    methods: {
        CreateSocket() {
            const vm = this;
            function MessageCallBack(SocketData) {
                var data = JSON.parse(SocketData);
                vm.SocketDataALL = data;
                vm.$store.commit('setSocketDataALL', vm.SocketDataALL, vm.CreateSocket);
            }

            if (vm.isDemo) {
                vm.SocketDataALL = vm.sucketDataDemo;
                vm.$store.commit('setSocketDataALL', vm.SocketDataALL);
            } else {
                const token = vm.$store.getters.user.Token;
                vm.webSocket = newwebsocket(MessageCallBack, null, null, null, token);
            }
        },
        
    },
};
</script>
<style scoped>
</style>