
<template>
    <teleport :disabled="!teleport" :to="teleport">
        <transition :name="animation">
            <div v-if="!transition" class="INVtable">
            <!-- {{ id }} -->
<div class="d-flex">

    <table class="text-center" style="border-collapse: separate; border-spacing: 0; width: 400px;border-color: #3081D0">
        <!-- <tr>
            <th class="text-start">INV</th>
        </tr> -->
        <tr>
            <td style="border: 1px solid ;">DC電壓</td>
            <td style="border: 1px solid ;">{{ props.data?.d?.toFixed(2)}}V</td>
            <td style="border: 1px solid ;">DC功率</td>
            <td style="border: 1px solid ;">{{ props.data?.a?.toFixed(2)}}kW</td>
        </tr>
        <tr>
            <td style="border: 1px solid ;">DC電流</td>
            <td style="border: 1px solid ;">{{ props.data?.b?.toFixed(2)}}A</td>
            <td style="border: 1px solid ;">溫度</td>
            <td style="border: 1px solid ;">{{ props.data?.c}}°C</td>
        </tr>
    </table>

</div>
    <!-- <Handle type="source" :position="Position.Bottom" /> -->
        </div>
        </transition>
    </teleport>
</template>

<script setup>

    import { Handle, Position } from '@braks/vue-flow'
    import { useTransition } from '@/lib/useTransition.js'
    
    const props = defineProps({
        id: {
            type: String,
            required: true,
        }, data: {
            type: Object
        },
    });
    
    const { animation, transition, teleport, onClick } = useTransition(props.id);
    const changeAnimation = () => {
    animation.value = animation.value === 'fade' ? 'shrink' : 'fade'
    };
    </script>
    
    <script>
    export default {
        inheritAttrs: false,
        data(){
            return{
            CBData:[
                {'TK':'Test','L/R':'Remote','Relay':'Trip','U':281.2,'I':205,'P':1192,'PF':0.97},
            ]
            }
        },
        }
    </script>
    