
    <template>
        <teleport :disabled="!teleport" :to="teleport">
        <transition :name="animation">
            <div v-if="!transition" class="DCUtable">
            <!-- {{ id }} -->
    <div class="d-flex">

    <table class="text-center px-3" style="border-collapse: separate; border-spacing: 0; width: 400px;border-color: #3081D0">
    <tr>
    <td style="border: 1px solid ;">AC功率</td>
    <td style="border: 1px solid ;">{{ props.data?.P?.toFixed(2) }}kW</td>
    <td style="border: 1px solid ;">電壓_ab</td>
    <td style="border: 1px solid ;">{{ props.data?.V_ab?.toFixed(2) }}V</td>
    </tr>
    <tr>
    <td style="border: 1px solid ;">電流</td>
    <td style="border: 1px solid ;">{{ props.data?.A?.toFixed(2) }}A</td>
    <td style="border: 1px solid ;">電壓_bc</td>
    <td style="border: 1px solid ;">{{ props.data?.V_bc?.toFixed(2) }}V</td>
    </tr>
    <tr>
    <td style="border: 1px solid ;">溫度</td>
    <td style="border: 1px solid ;">{{ props.data?.T?.toFixed(2) }}°C</td>
    <td style="border: 1px solid ;">電壓_ca</td>
    <td style="border: 1px solid ;">{{ props.data?.V_ca?.toFixed(2) }}V</td>
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
        