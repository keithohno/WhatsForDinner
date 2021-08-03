<template>
  <tr>
    <th scope="row">{{ name }}</th>
    <td>{{ amount }}</td>
    <td>{{ unit }}</td>
    <td>{{ mod }}</td>
  </tr>
</template>

<script>
export default {
  name: "Ingredient",
  props: {
    name: String,
    amount: Number,
    unit: String,
    mod: String,
  },
};
</script>