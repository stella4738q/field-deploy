    <template>
        <teleport :disabled="!teleport" :to="teleport">
        <transition :name="animation">
            <div v-if="!transition" class="Relaytable">
            <!-- {{ id }} -->
    <div class="d-flex">

    <table class="text-center px-3" style="border-collapse: separate; border-spacing: 0; width: 300px;border-color: #3081D0" v-if="props.data.TK != 'NaN' && props.data.LR != 'NaN'  && props.data.TRIP != 'NaN'  ">
    <tr>
    <td style="border: 1px solid ;">TK</td>
    <td style="border: 1px solid ;">{{ props.data.TK }}</td>
    </tr>
    <tr>
    <td style="border: 1px solid ;">L/R</td>
    <td style="border: 1px solid ;">{{ props.data.LR }}</td>
    </tr>
    <tr>
    <td style="border: 1px solid ;">Relay</td>
    <td style="border: 1px solid ;">{{ props.data.TRIP }}</td>
    </tr>

    </table>

    </div>
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


    const { animation, transition, teleport, onClick } = useTransition(props);
    const changeAnimation = () => {
    animation.value = animation.value === 'fade' ? 'shrink' : 'fade'
    };
    </script>
        
    <script>
    export default {
    data() {
        return {

        }
    },
    }
    </script>
        