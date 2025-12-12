
    <template>
        <teleport :disabled="!teleport" :to="teleport">
        <transition :name="animation">
            <div v-if="!transition" class="TRtable">
            <!-- {{ id }} -->
    <div class="d-flex">

    <table class="text-center px-3" style="border-collapse: separate; border-spacing: 0; width: 300px;border-color: #3081D0">
    <tr>
    <td style="border: 1px solid ;">溫度</td>
    <td style="border: 1px solid ;">{{ props.data?.temperature}}°C</td>
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
        