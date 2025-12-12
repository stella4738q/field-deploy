<template>
    <h1>welcome~</h1>
</template>

<script >

    export default {
        components: {
        },
        data() {
            return { }
        },
        created() {
            let UserName = window.localStorage.getItem("name");
            if (UserName) {
                if (UserName.toLocaleLowerCase() === 'coach') {
                    this.$router.push({ name: 'CoachMember'});
                } else if (UserName.toLocaleLowerCase() === 'marketing') {
                    this.$router.push({ name: 'Leads' });

                } else if (UserName.toLocaleLowerCase() === 'ADMIN') {
                    this.$router.push({ name: 'CoachMember' });
                }
            }
        },
        watch: {
        },
        methods: {
             
        },
    };
</script>
<style>
</style>