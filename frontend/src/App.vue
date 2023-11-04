<script setup lang="ts">
import { isReactive, ref } from 'vue'
import { Backend } from './backend'

const backend = ref(new Backend())
const complaintText = ref("")
const pathwayResults = ref<Array<any>>([])
const outputText = ref("")
const stepitems = ref<Array<any>>([{number: 1, label: 'Enter your complaint'}, {number: 2, label: 'Select the pathway'}, {number: 3, label: 'Finish'}])
const activeStep = ref(1)
const spinning = ref(false)

function isActive(item: any) {
  console.log('isactive: item', item, 'activeStep', activeStep.value)
  return item.number == activeStep.value
}

async function onSubmit() {
  const request = {
    complaint: complaintText.value
  }
  activeStep.value = 2
  spinning.value = true
  const response = await backend.value.rpcClient.request('stage2_submit', request)
  spinning.value = false
  pathwayResults.value = response
  console.log('result:', pathwayResults.value)
}


async function onGenerate(id: string) {
  const request = {
    complaint: complaintText.value,
    id
  }
  activeStep.value = 3
  spinning.value = true
  const response = await backend.value.rpcClient.request('generate', request)
  spinning.value = false
  if (response?.output) {
    outputText.value = response.output
  }
}
</script>

<template>
  <header class="text-2xl font-bold">
    ComplainToUs
  </header>

  <main>
    <Steps :model="stepitems" aria-label="Form Steps" readonly
        :pt="{
            menuitem: ({ context }) => ({
                class: isActive(context.item) && 'p-highlight p-steps-current'
            })
        }">
        <template #item="{ label, item, index, props }">
            <span v-bind="props.action">
                <span v-bind="props">{{ index + 1 }}</span>
                <span v-bind="props.label">{{ label }}</span>
            </span>
        </template>
    </Steps>
    <div v-if="activeStep == 1">
      <div class="text-xl font-bold my-8">Please tell us your complaint in two or more lines:</div>
      <div class="p-float-label">
        <TextArea id="complaint-text" v-model="complaintText" rows="5" cols="72" autoResize />
        <label>Your Complaint</label>
      </div>
      <div>
        <Button label="Submit" @click="onSubmit"/>
      </div>
    </div>
    <div v-else-if="activeStep == 2">
      <div class="text-xl font-bold my-8">You have the following options for your complaint</div>
      <ProgressSpinner v-if="spinning" />
      <div v-for="pathway in pathwayResults" class="my-4">
        <div class="text-xl font-bold my-4">{{ pathway.name }}</div>
        <div class="my-2">{{ pathway.descr }}</div>
        <div class="my-2">You can use this option for the following reason:</div>
        <div class="my-2"> {{ pathway.reason }}</div>
        <div class="my-4"><Button :label="'Create a complaint to ' + pathway.name" @click="onGenerate(pathway.id)"/></div>
      </div>
    </div>
    <div v-else class="my-12">
      <header class="text-xl font-bold my-4">Here is your complaint</header>
      <ProgressSpinner v-if="spinning" />
      <span class="whitespace-pre-line my-2">
        {{ outputText  }}
      </span>
    </div>
  </main>
</template>

<style scoped>
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
