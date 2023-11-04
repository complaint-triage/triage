
import { createApp } from 'vue'
import Button from 'primevue/button'
import PrimeVue from 'primevue/config'
import ProgressSpinner from 'primevue/progressspinner'
import Steps from 'primevue/steps'
import TextArea from 'primevue/textarea'
import App from './App.vue'

import './assets/main.css'
import 'primevue/resources/themes/saga-blue/theme.css'

createApp(App)
    .use(PrimeVue, { ripple: false })
    .component('Button', Button)
    .component('ProgressSpinner', ProgressSpinner)   
    .component('Steps', Steps)
    .component('TextArea', TextArea)
    .mount('#app')
