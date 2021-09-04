<template>
  <p>Search by Ingredient:</p>
  <div class="query-form">
    <div
      v-for="(ingredient, index) in ingredients"
      :key="index"
      class="input-group mb-1"
    >
      <input
        :value="ingredient"
        @input="(e) => edit_ingredient(index, e.target.value)"
        class="form-control"
      />
      <span class="input-spacer">
        <button
          class="btn btn-outline-secondary del-btn"
          @click="(e) => remove_ingredient(index)"
        >
          <img src="../../public/x.png" class="my-icon" />
        </button>
      </span>
    </div>
    <div class="query-actions btn-group d-flex">
      <button
        class="btn btn-outline-secondary plus-btn"
        @click="add_ingredient"
      >
        <img src="../../public/plus.png" class="my-icon" />
      </button>
      <button class="btn btn-outline-secondary search-btn" @click="query">
        <img src="../../public/search.png" class="my-icon" />
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "QueryOptions",
  computed: {
    count() {
      return this.$store.state.count;
    },
    ingredients() {
      return this.$store.state.ingredients;
    },
  },
  methods: {
    add_ingredient() {
      this.$store.commit("add_ingredient", "");
    },
    remove_ingredient(index) {
      this.$store.commit("remove_ingredient", index);
    },
    edit_ingredient(index, value) {
      this.$store.commit("edit_ingredient", { index, value });
    },
    query() {
      this.$emit("query");
    },
  },
};
</script>

<style scoped>
.my-icon {
  width: 22px;
}
.plus-btn,
.del-btn,
.search-btn {
  border: 2px solid white;
  background-color: #f2f2f2;
}
.plus-btn:hover {
  background-color: #ced;
  border-color: #ced;
}
.search-btn:hover {
  background-color: #cdf;
  border-color: #cdf;
}
.del-btn:hover {
  background-color: #faa;
  border-color: #faa;
}
.input-spacer {
  padding-left: 5px;
}
.form-control:focus {
  border: 2px solid #bdf;
  box-shadow: 0px 0px white;
}
</style>